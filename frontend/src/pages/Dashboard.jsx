import { useEffect, useState } from 'react'
import { BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import KpiCard from '../components/KpiCard'
import { fetchDashboard, uploadMeeting } from '../services/api'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [text, setText] = useState('- PM to finalize weekly status update\n- Vendor to resolve API blocker urgently')

  const load = async () => setData(await fetchDashboard())
  useEffect(() => {
    load()
  }, [])

  const ownerSeries = Object.entries(data?.by_owner || {}).map(([owner, count]) => ({ owner, count }))

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', padding: 20, background: '#f4f6fa', minHeight: '100vh' }}>
      <h1>VigorousONE AI PMO Control Tower</h1>
      <div style={{ display: 'grid', gap: 12, gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
        <KpiCard label="Total Tasks" value={data?.total_tasks ?? '-'} />
        <KpiCard label="Completed" value={data?.completed_tasks ?? '-'} />
        <KpiCard label="Pending" value={data?.pending_tasks ?? '-'} />
        <KpiCard label="Overdue" value={data?.overdue_tasks ?? '-'} />
      </div>

      <section style={{ marginTop: 20, background: '#fff', padding: 16, borderRadius: 12 }}>
        <h2>Stakeholder Performance</h2>
        <div style={{ width: '100%', height: 240 }}>
          <ResponsiveContainer>
            <BarChart data={ownerSeries}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="owner" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#0f766e" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section style={{ marginTop: 20, background: '#fff', padding: 16, borderRadius: 12 }}>
        <h2>AI Input Ingestion</h2>
        <textarea rows={5} style={{ width: '100%' }} value={text} onChange={(e) => setText(e.target.value)} />
        <button
          onClick={async () => {
            await uploadMeeting({ project_id: 1, input_type: 'meeting', text, filename: 'live-note.txt' })
            await load()
          }}
        >
          Extract Tasks + Generate MoM
        </button>
      </section>
    </div>
  )
}
