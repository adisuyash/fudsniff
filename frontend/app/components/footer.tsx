import React from "react";

const Footer = () => {
  return (
    <footer className="py-6 text-center text-xs sm:text-sm text-gray-500 font-[family-name:var(--font-geist-sans)] tracking-widest">
      <div className="hidden sm:inline">
        Built by{" "}
        <a
          href="https://x.com/adisuyash"
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-400 hover:text-white transition-colors duration-200 underline-offset-4 hover:underline"
        >
          AdiSuyash
        </a>
        {" ⚡ "}Powered by{" "}
        <a
          href="https://superioragents.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-400 hover:text-white transition-colors duration-200 underline-offset-4 hover:underline"
        >
          Superior Agents
        </a>
        {" 💛"}
      </div>

      <div className="sm:hidden space-y-1">
        <div>
          Built by{" "}
          <a
            href="https://x.com/adisuyash"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-400 hover:text-white transition-colors duration-200 underline-offset-4 hover:underline"
          >
            AdiSuyash
          </a>{" "}
          ⚡
        </div>
        <div>
          Powered by{" "}
          <a
            href="https://superioragents.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-400 hover:text-white transition-colors duration-200 underline-offset-4 hover:underline"
          >
            Superior Agents
          </a>{" "}
          💛
        </div>
      </div>
    </footer>
  );
};

export default Footer;
