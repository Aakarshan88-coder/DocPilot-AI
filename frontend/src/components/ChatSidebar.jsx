function ChatSidebar({ onNewChat, children }) {
  return (
    <aside className="chat-sidebar">
      <div className="chat-sidebar-header">
        <div>
          <span className="sidebar-eyebrow">Workspace</span>
          <h2>Conversations</h2>
        </div>

        <button className="new-chat-button" type="button" onClick={onNewChat}>
          + New chat
        </button>
      </div>

      {children}
    </aside>
  );
}

export default ChatSidebar;
