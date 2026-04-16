export default function KpiCard({ label, value }) {
  return (
    <div style={{ background: '#111827', color: '#fff', padding: 16, borderRadius: 10 }}>
      <div style={{ fontSize: 13, opacity: 0.75 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700 }}>{value}</div>
    </div>
  )
}
