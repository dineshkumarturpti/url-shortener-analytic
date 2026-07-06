export default function LinkList({ links, onSelect, selectedCode }) {
  if (links.length === 0) {
    return <p className="empty-state">No links yet — shorten one above to get started.</p>;
  }

  return (
    <ul className="link-list">
      {links.map((link) => (
        <li
          key={link.short_code}
          className={link.short_code === selectedCode ? "link-item selected" : "link-item"}
          onClick={() => onSelect(link.short_code)}
        >
          <div className="link-item-main">
            <span className="short-url">{link.short_url}</span>
            <span className="long-url">{link.long_url}</span>
          </div>
          <button
            type="button"
            onClick={(event) => {
              event.stopPropagation();
              navigator.clipboard.writeText(link.short_url);
            }}
          >
            Copy
          </button>
        </li>
      ))}
    </ul>
  );
}
