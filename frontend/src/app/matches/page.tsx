'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export default function MatchesPage() {
  const router = useRouter()
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }

    fetchMatches()
  }, [router])

  const fetchMatches = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/matches`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setMatches(data)
      }
    } catch (error) {
      console.error('Error fetching matches:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const badges: any = {
      'pending': 'bg-gray-100 text-gray-800',
      'uploading': 'bg-blue-100 text-blue-800',
      'processing': 'bg-yellow-100 text-yellow-800',
      'analyzing': 'bg-purple-100 text-purple-800',
      'completed': 'bg-green-100 text-green-800',
      'failed': 'bg-red-100 text-red-800'
    }
    
    const labels: any = {
      'pending': 'Bekliyor',
      'uploading': 'Yükleniyor',
      'processing': 'İşleniyor',
      'analyzing': 'Analiz Ediliyor',
      'completed': 'Tamamlandı',
      'failed': 'Başarısız'
    }

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${badges[status] || badges.pending}`}>
        {labels[status] || status}
      </span>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-primary-700">Maçlar</h1>
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/dashboard')}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Dashboard
            </button>
            <button
              onClick={() => router.push('/matches/new')}
              className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
            >
              + Yeni Maç
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="text-gray-500">Yükleniyor...</div>
          </div>
        ) : matches.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-6xl mb-4">⚽</div>
            <h3 className="text-xl font-medium text-gray-900 mb-2">
              Henüz maç bulunmuyor
            </h3>
            <p className="text-gray-500 mb-6">
              İlk maçınızı ekleyerek analiz sürecini başlatın
            </p>
            <button
              onClick={() => router.push('/matches/new')}
              className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700"
            >
              Yeni Maç Ekle
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {matches.map((match: any) => (
              <div
                key={match.id}
                onClick={() => router.push(`/matches/${match.id}`)}
                className="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer"
              >
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-bold text-lg text-gray-900">
                        vs {match.opponent_name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {new Date(match.match_date).toLocaleDateString('tr-TR')}
                      </p>
                    </div>
                    {getStatusBadge(match.status)}
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Lokasyon:</span>
                      <span className="font-medium">{match.location}</span>
                    </div>
                    {match.final_score_home !== null && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Skor:</span>
                        <span className="font-medium">
                          {match.final_score_home} - {match.final_score_away}
                        </span>
                      </div>
                    )}
                  </div>

                  {match.status === 'completed' && (
                    <div className="mt-4 pt-4 border-t">
                      <button className="text-primary-600 text-sm font-medium hover:text-primary-700">
                        Analizi Görüntüle →
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
