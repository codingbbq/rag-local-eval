import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import '../styles/MarkdownContent.css';

function MarkdownContent({ content }) {
  return (
    <div className="markdown-content">
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({node, ...props}) => <h1 className="md-h1" {...props} />,
          h2: ({node, ...props}) => <h2 className="md-h2" {...props} />,
          h3: ({node, ...props}) => <h3 className="md-h3" {...props} />,
          h4: ({node, ...props}) => <h4 className="md-h4" {...props} />,
          p: ({node, ...props}) => <p className="md-p" {...props} />,
          ul: ({node, ...props}) => <ul className="md-ul" {...props} />,
          ol: ({node, ...props}) => <ol className="md-ol" {...props} />,
          li: ({node, ...props}) => <li className="md-li" {...props} />,
          code: ({node, inline, ...props}) => 
            inline ? (
              <code className="md-inline-code" {...props} />
            ) : (
              <pre className="md-code-block">
                <code {...props} />
              </pre>
            ),
          blockquote: ({node, ...props}) => <blockquote className="md-blockquote" {...props} />,
          a: ({node, ...props}) => <a className="md-link" {...props} />,
          table: ({node, ...props}) => <table className="md-table" {...props} />,
          th: ({node, ...props}) => <th className="md-th" {...props} />,
          td: ({node, ...props}) => <td className="md-td" {...props} />,
          hr: ({node, ...props}) => <hr className="md-hr" {...props} />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

export default MarkdownContent;
