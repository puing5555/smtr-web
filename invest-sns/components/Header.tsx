'use client'

export default function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 bg-[#0a0a0a] border-b border-gray-800 z-50">
      <div className="max-w-[480px] mx-auto px-4 py-3 flex items-center justify-between">
        <h1 className="text-xl font-bold text-white">투자SNS</h1>
        <div className="flex items-center gap-4">
          <button className="text-gray-300 hover:text-white">
            🔔
          </button>
          <button className="text-gray-300 hover:text-white">
            🔍
          </button>
        </div>
      </div>
    </header>
  )
}