'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [stats, setStats] = useState({
    totalMatches: 0,
    completedAnalyses: 0,
    totalPlayers: 0,
    avgPossession: 0
  })

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }

    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
    }

    // Mock stats
    setStats({
      totalMatches: 12,
      completedAnalyses: 10,
      totalPlayers: 18,
      avgPossession: 54.3
    })
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-primary-700">PitchVision Lite</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-700">{user.full_name}</span>
            <button
              onClick={handleLogout}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Çıkış
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600 mb-1">Toplam Maç</div>
            <div className="text-3xl font-bold text-primary-600">{stats.totalMatches}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600 mb-1">Tamamlanan Analiz</div>
            <div className="text-3xl font-bold text-green-600">{stats.completedAnalyses}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600 mb-1">Toplam Oyuncu</div>
            <div className="text-3xl font-bold text-blue-600">{stats.totalPlayers}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600 mb-1">Ort. Top Hakimiyeti</div>
            <div className="text-3xl font-bold text-purple-600">%{stats.avgPossession}</div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Hızlı İşlemler</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => router.push('/matches/new')}
              className="p-4 border-2 border-primary-200 rounded-lg hover:border-primary-400 hover:bg-primary-50 transition"
            >
              <div className="text-4xl mb-2">📹</div>
              <div className="font-medium">Yeni Maç Yükle</div>
            </button>
            <button
              onClick={() => router.push('/matches')}
              className="p-4 border-2 border-gray-200 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition"
            >
              <div className="text-4xl mb-2">📊</div>
              <div className="font-medium">Maçları Görüntüle</div>
            </button>
            <button
              onClick={() => router.push('/players')}
              className="p-4 border-2 border-gray-200 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition"
            >
              <div className="text-4xl mb-2">👥</div>
              <div className="font-medium">Oyuncular</div>
            </button>
          </div>
        </div>

        {/* Recent Matches */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Son Maçlar</h2>
          <div className="text-gray-500 text-center py-8">
            Henüz maç bulunmuyor. Yeni maç eklemek için yukarıdaki butonu kullanın.
          </div>
        </div>
      </main>
    </div>
  )
}
