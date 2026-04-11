import React, { createContext, useState } from "react";

export const EnergyContext = createContext(null);

export function EnergyProvider({ children }) {
  const [energyData, setEnergyData] = useState([]);
  return (
    <EnergyContext.Provider value={{ energyData, setEnergyData }}>
      {children}
    </EnergyContext.Provider>
  );
}
