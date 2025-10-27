import React from "react";

export default function PasswordStrength({ password }) {
  const getStrength = () => {
    let score = 0;
    if (password.length > 5) score++;
    if (password.length > 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return score;
  };

  const strength = getStrength();
  const colors = ["bg-red-500", "bg-orange-500", "bg-yellow-400", "bg-green-400", "bg-green-600"];
  const text = ["Weak", "Fair", "Good", "Strong", "Very Strong"];

  return (
    <div className="mt-3">
      <div className="flex space-x-1">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className={`h-2 w-1/5 rounded ${i < strength ? colors[strength - 1] : "bg-gray-200"}`}
          ></div>
        ))}
      </div>
      {password && (
        <p className="text-sm text-gray-500 mt-1">{text[strength - 1] || "Too short"}</p>
      )}
    </div>
  );
}
