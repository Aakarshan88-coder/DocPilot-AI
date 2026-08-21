function SuggestedQuestions({ questions, onSelect, disabled }) {
  return (
    <div className="suggested-questions">
      <div className="suggested-questions-title">Try asking</div>

      <div className="suggested-questions-list">
        {questions.map((question) => (
          <button
            key={question}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(question)}
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}

export default SuggestedQuestions;
