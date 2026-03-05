import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function OptionsChart({ callVolume = 0, putVolume = 0, putCallRatio = 0 }) {
  const data = {
    labels: ['콜 거래량', '풋 거래량'],
    datasets: [
      {
        data: [callVolume || 0, putVolume || 0],
        backgroundColor: ['#22c55e', '#ef4444'],
        borderWidth: 0,
      },
    ],
  };
  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'bottom' },
    },
  };
  return (
    <div>
      <Doughnut data={data} options={options} />
      <p className="text-center text-sm text-gray-600 mt-2">풋/콜 비율: {putCallRatio?.toFixed(2) ?? '-'}</p>
    </div>
  );
}
