import React, { useState, useEffect } from 'react';

// Scramble Text effect for status updates
export default function ScrambleText({ text, active }) {
  const [displayText, setDisplayText] = useState(text);
  const chars = '!<>-_\\\\/[]{}—=+*^?#________';

  useEffect(() => {
    if (!active) {
      setDisplayText(text);
      return;
    }

    let iteration = 0;
    const interval = setInterval(() => {
      setDisplayText((old) =>
        text
          .split('')
          .map((letter, index) => {
            if (index < iteration) return text[index];
            return chars[Math.floor(Math.random() * chars.length)];
          })
          .join('')
      );

      if (iteration >= text.length) {
        clearInterval(interval);
      }
      iteration += 1 / 3;
    }, 30);

    return () => clearInterval(interval);
  }, [text, active]);

  return <span>{displayText}</span>;
}
