function SourceCitations({ sources = [] }) {
  if (sources.length === 0) {
    return null;
  }

  return (
    <div className="source-citations">
      <div className="source-citations-title">Sources</div>

      <div className="source-citations-list">
        {sources.map((source, index) => {
          const pageLabel = source.page_number
            ? `Page ${source.page_number}`
            : "Document source";

          const snippet = source.chunk?.replace(/\s+/g, " ").trim();

          return (
            <div
              className="source-citation"
              key={`${source.page_number || "source"}-${source.chunk_index ?? index}`}
            >
              <span className="source-citation-page">{pageLabel}</span>
              <span className="source-citation-text">
                {snippet
                  ? `${snippet.slice(0, 180)}${snippet.length > 180 ? "..." : ""}`
                  : "Referenced document content"}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default SourceCitations;
