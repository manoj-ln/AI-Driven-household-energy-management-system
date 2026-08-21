import React, { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { getDatasetMode, getDatasets, selectDataset, setDatasetMode } from "../services/apiService";

export const EnergyContext = createContext(null);

function prettifyDatasetName(filename = "") {
  return filename
    .replace(/\.csv$/i, "")
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function EnergyProvider({ children, authenticated = false }) {
  const [datasetState, setDatasetState] = useState({
    mode: "auto",
    selectedDataset: "",
    datasets: [],
    details: null,
    loading: true,
    error: "",
  });

  const refreshDatasetState = useCallback(async () => {
    if (!authenticated) {
      setDatasetState((prev) => ({ ...prev, loading: false, error: "" }));
      return null;
    }
    setDatasetState((prev) => ({ ...prev, loading: true, error: "" }));
    let modeResponse;
    let datasetsResponse;
    for (let attempt = 0; attempt < 3; attempt += 1) {
      [modeResponse, datasetsResponse] = await Promise.all([getDatasetMode(), getDatasets()]);
      if (modeResponse && datasetsResponse) {
        break;
      }
      await new Promise((resolve) => window.setTimeout(resolve, 1000));
    }

    if (!modeResponse || !datasetsResponse) {
      setDatasetState((prev) => ({
        ...prev,
        loading: false,
        error: "Dataset endpoints are not responding.",
      }));
      return null;
    }

    const datasets = Array.isArray(datasetsResponse.datasets) ? datasetsResponse.datasets : [];
    const selectedDataset = modeResponse.selected_dataset || datasetsResponse.selected_dataset || datasets[0] || "";
    const details = modeResponse.dataset_details || null;

    const nextState = {
      mode: modeResponse.mode || "auto",
      selectedDataset,
      datasets,
      details,
      loading: false,
      error: "",
    };
    setDatasetState(nextState);
    return nextState;
  }, [authenticated]);

  useEffect(() => {
    refreshDatasetState();
  }, [authenticated, refreshDatasetState]);

  const applyDatasetSelection = useCallback(
    async (datasetName) => {
      const selection = await selectDataset(datasetName);
      if (!selection?.status || selection.status !== "success") {
        return selection;
      }
      await setDatasetMode("synthetic_demo");
      await refreshDatasetState();
      return selection;
    },
    [refreshDatasetState]
  );

  const value = useMemo(
    () => ({
      datasetState,
      refreshDatasetState,
      applyDatasetSelection,
      activeDatasetLabel: datasetState.selectedDataset ? prettifyDatasetName(datasetState.selectedDataset) : "Loading dataset",
    }),
    [applyDatasetSelection, datasetState, refreshDatasetState]
  );

  return <EnergyContext.Provider value={value}>{children}</EnergyContext.Provider>;
}
