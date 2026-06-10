import { useEffect, useState } from "react";
import api from "../lib/api";
import Navbar from "../components/Navbar";
import GameCard from "../components/GameCard";
import { Footer } from "./Home";
import { Search, Clock } from "lucide-react";

export default function ComingSoon() {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.get("/games?status=coming_soon").then((r) => {
      setGames(r.data); setLoading(false);
    });
  }, []);

  const filtered = games.filter((g) => !search || g.title.toLowerCase().includes(search.toLowerCase()));

  return (
    <div dir="rtl" className="min-h-screen">
      <Navbar />
      <section className="max-w-7xl mx-auto px-6 pt-16 pb-12 relative">
        <div className="absolute inset-0 grid-pattern" />
        <div className="ornament mb-6"><Clock size={14}/> <span className="text-xs tracking-[0.3em]">COMING SOON</span></div>
        <h1 className="heading-ar text-5xl sm:text-6xl text-center mb-4">
          ألعاب <span className="gold-text">قادمة قريباً</span>
        </h1>
        <p className="text-center text-slate-400 max-w-2xl mx-auto mb-10 text-sm">
          ألعاب لم تُطلق بعد على Steam — سيتم إضافة روابط الكراك فور توفرها.
        </p>

        <div className="relative max-w-xl mx-auto mb-10">
          <Search size={16} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            value={search} onChange={(e)=>setSearch(e.target.value)}
            placeholder="ابحث في الألعاب القادمة..."
            className="w-full pr-11 pl-4 py-3.5 rounded-xl bg-[#07101e] border border-[rgba(229,181,88,0.15)] focus:border-[#e5b558]/50 outline-none text-sm"
            data-testid="coming-search"
          />
        </div>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {Array.from({length:6}).map((_,i)=><div key={`sk-${i}`} className="aspect-[460/300] rounded-2xl shimmer bg-[#0c1729]" />)}
          </div>
        ) : filtered.length === 0 ? (
          <div className="glass rounded-2xl p-12 text-center text-slate-400">
            لا توجد ألعاب قادمة حالياً. تابعنا للجديد قريباً.
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {filtered.map((g)=><GameCard key={g.id} game={g} />)}
          </div>
        )}
      </section>
      <Footer />
    </div>
  );
}
