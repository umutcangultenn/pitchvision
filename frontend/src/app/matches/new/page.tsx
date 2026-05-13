'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function NewMatchPage() {
  const router = useRouter()
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    team_id: '',
    opponent_name: '',
    match_date: '',
    location: '',
    home_away: 'Ev Sahibi',
    duration_minutes: 90
  })

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }

    fetchTeams()
  }, [router])

  const fetchTeams = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/teams`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setTeams(data)
        if (data.length > 0) {
          setFormData(prev => ({ ...prev, team_id: data[0].id.toString() }))
        }
      }
    } catch (error) {
      console.error('Error fetching teams:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/matches`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          team_id: parseInt(formData.team_id),
          match_date: new Date(formData.match_date).toISOString()
        })
      })

      if (response.ok) {
        const match = await response.json()
        router.push(`/matches/${match.id}`)
      } else {
        alert('Maç oluşturulamadı')
      }
    } catch (error) {
      console.error('Error creating match:', error)
      alert('Bir hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => router.back()}
            className="text-gray-600 hover:text-gray-900 mb-2"
          >
            ← Geri
          </button>
          <h1 className="text-2xl font-bold text-primary-700">Yeni Maç Ekle</h1>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Takım
              </label>
              <select
                value={formData.team_id}
                onChange={(e) => setFormData({ ...formData, team_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                required
              >
                {teams.map((team: any) => (
                  <option key={team.id} value={team.id}>
                    {team.name} ({team.age_group})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rakip Takım
              </label>
              <input
                type="text"
                value={formData.opponent_name}
                onChange={(e) => setFormData({ ...formData, opponent_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="Örnek Spor Kulübü"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Maç Tarihi
                </label>
                <input
                  type="datetime-local"
                  value={formData.match_date}
                  onChange={(e) => setFormData({ ...formData, match_date: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ev/Deplasman
                </label>
                <select
                  value={formData.home_away}
                  onChange={(e) => setFormData({ ...formData, home_away: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option>Ev Sahibi</option>
                  <option>Deplasman</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lokasyon
              </label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="Ana Saha"
                required
              />
            </div>

            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => router.back()}
                className="flex-1 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                İptal
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {loading ? 'Oluşturuluyor...' : 'Maç Oluştur'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  )
}
