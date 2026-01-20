// src/components/ChatInput.jsx
export default function ChatInput() {
  return (
    <div className="flex items-center p-2 bg-ci-dark border-t border-ci-void">
      <label className="cursor-pointer p-2 hover:text-ci-gold transition-colors">
        <input type="file" className="hidden" accept="image/*" 
               onChange={(e) => handleUpload(e.target.files[0])} />
        <span>📸 Додати Магію</span>
      </label>
      <input type="text" placeholder="Опишіть подію..." 
             className="flex-1 bg-transparent border-none focus:ring-0 text-sm" />
    </div>
  );
}