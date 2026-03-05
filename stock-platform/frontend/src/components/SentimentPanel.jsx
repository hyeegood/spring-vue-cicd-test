export default function SentimentPanel({ news }) {
  if (!news?.length) return <p className="text-gray-500">뉴스 없음</p>;
  return (
    <ul className="space-y-2">
      {news.map((n, i) => (
        <li key={i} className="border-b border-gray-100 pb-2">
          <a href={n.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline block">
            {n.title}
          </a>
          <span className="text-sm text-gray-500">
            감성: {(n.sentiment ?? 0).toFixed(2)} {n.date ? new Date(n.date).toLocaleDateString('ko-KR') : ''}
          </span>
        </li>
      ))}
    </ul>
  );
}
