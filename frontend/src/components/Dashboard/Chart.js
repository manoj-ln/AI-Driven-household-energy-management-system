import React from "react";
import { Bar, Line } from "react-chartjs-2";
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

function Chart({
  labels = [],
  values = [],
  datasetLabel = "Energy (kWh)",
  borderColor = "#0f4c81",
  backgroundColor = "rgba(15, 76, 129, 0.18)",
  chartType = "line",
  yAxisLabel = "Energy (kWh)",
  extraDatasets = [],
}) {
  const safeLabels = labels.length ? labels : ["6 AM", "9 AM", "12 PM", "3 PM", "6 PM", "9 PM"];
  const safeValues = values.length ? values : [1.5, 2.1, 1.9, 2.5, 3.2, 2.8];
  const data = {
    labels: safeLabels,
    datasets: [
      {
        label: datasetLabel,
        data: safeValues,
        backgroundColor,
        borderColor,
        tension: 0.35,
        fill: chartType !== "bar",
        pointRadius: chartType === "bar" ? 0 : 2,
        pointHoverRadius: chartType === "bar" ? 0 : 4,
        borderWidth: 2,
      },
      ...extraDatasets,
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "top",
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.dataset.label}: ${context.parsed.y}`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: yAxisLabel,
        },
      },
    },
  };

  return (
    <div style={{ height: "280px" }}>
      {chartType === "bar" ? <Bar data={data} options={options} /> : <Line data={data} options={options} />}
    </div>
  );
}

export default Chart;
