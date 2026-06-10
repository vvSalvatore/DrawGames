import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import api from "../lib/api";
import Navbar from "../components/Navbar";
import GameCard from "../components/GameCard";
import { Search, Filter, Sparkles, Library, Users, Wifi, ArrowLeft } from "lucide-react";

const COOP_FILTERS = [
  { id: "all", label: "كل الألعاب" },
  { id: "coop", label: "تعاوني (Co-op)" },
  { id: "multi", label: "متعدد اللاعبين" },
  { id: "solo", label: "لاعب واحد" },
];

export default function Home() {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [search, setSearch] = useState("");
  const [genre, setGenre] = useState("All");
  const [coopFilter, setCoopFilter] = useState("all");
  const [allGenres, setAllGenres] = useState([]);

  useEffect(() => {
    (async () => {
      const [g, s, gns] = await Promise.all([
        api.get("/games?status=cracked"),
        api.get("/games/stats"),
        api.get("/games/genres"),
      ]);
      setGames(g.data); setStats(s.data); setAllGenres(gns.data);
      setLoading(false);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const genres = useMemo(
    () => ["All", ...allGenres.slice(0, 12).map((x) => x.name)],
    [allGenres]
  );

  const filtered = useMemo(() => {
    return games.filter((g) => {
      if (search && !g.title.toLowerCase().includes(search.toLowerCase())) return false;
      if (genre !== "All" && !g.genres?.includes(genre)) return false;
      if (coopFilter === "coop" && !g.is_coop) return false;
      if (coopFilter === "multi" && !g.is_multiplayer) return false;
      if (coopFilter === "solo" && (g.is_coop || g.is_multiplayer)) return false;
      return true;
    });
  }, [games, search, genre, coopFilter]);

  return (
    <div dir="rtl" className="min-h-screen">
      <Navbar />
      {/* Hero */}
      <section className="relative">
        <div className="absolute inset-0 grid-pattern" />
        <div className="max-w-7xl mx-auto px-6 pt-16 pb-12 relative">
          <div className="ornament mb-6 fade-up">
            <span className="text-xs tracking-[0.3em]">★ DRAWCRACK ★</span>
          </div>
          <h1 className="heading-ar text-5xl sm:text-6xl lg:text-7xl text-center mb-4 fade-up">
            مكتبة <span className="gold-text">أسطورية</span> للألعاب
          </h1>
          <p className="text-center text-slate-400 max-w-2xl mx-auto mb-8 leading-relaxed fade-up text-sm sm:text-base">
            تحميل الألعاب المكركة بأعلى جودة من <span className="text-[#e5b558] font-bold">FitGirl</span>، <span className="text-[#3b82f6] font-bold">Online-Fix</span>، <span className="text-[#10b981] font-bold">AnkerGames</span> و <span className="text-[#06b6d4] font-bold">SteamUnlocked</span> مع شروحات تفصيلية وتقييمات Steam حقيقية.
          </p>

          {/* Stats strip */}
          {stats && (
            <div className="flex flex-wrap items-center justify-center gap-3 mb-10 fade-up" data-testid="hero-stats">
              <Stat label="إجمالي" value={stats.total} />
              <Stat label="مكركة" value={stats.cracked} accent="#10b981" />
              <Stat label="قادمة" value={stats.coming_soon} accent="#b91c1c" />
              <Stat label="تعاونية" value={stats.coop} accent="#e5b558" />
            </div>
          )}

          {/* Search + filters */}
          <div className="glass-gold rounded-2xl p-4 sm:p-6 max-w-5xl mx-auto">
            <div className="relative mb-4">
              <Search size={16} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="ابحث عن لعبة..."
                className="w-full pr-11 pl-4 py-3.5 rounded-xl bg-[#07101e] border border-[rgba(229,181,88,0.15)] focus:border-[#e5b558]/50 outline-none text-sm transition"
                data-testid="home-search-input"
              />
            </div>

            <div className="space-y-3">
              <Row label="نوع اللعب">
                {COOP_FILTERS.map((c) => (
                  <FilterPill key={c.id} active={coopFilter === c.id} onClick={() => setCoopFilter(c.id)} testid={`filter-coop-${c.id}`}>
                    {c.label}
                  </FilterPill>
                ))}
              </Row>
              <Row label="التصنيف">
                {genres.map((g) => (
                  <FilterPill key={g} active={genre === g} onClick={() => setGenre(g)} testid={`filter-genre-${g}`}>
                    {g === "All" ? "الكل" : g}
                  </FilterPill>
                ))}
              </Row>
            </div>
          </div>
        </div>
      </section>

      {/* Games grid */}
      <section className="max-w-7xl mx-auto px-6 pb-20">
        <div className="flex items-center justify-between mb-6">
          <h2 className="heading-ar text-2xl flex items-center gap-2">
            <Library size={20} className="text-[#e5b558]" /> مكتبة الألعاب
            <span className="text-sm text-slate-500 font-normal">({filtered.length})</span>
          </h2>
          <Link to="/coming-soon" className="text-sm text-[#e5b558] hover:text-[#f4d57d] flex items-center gap-1" data-testid="home-link-coming">
            الألعاب القادمة <ArrowLeft size={14} />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={`sk-${i}`} className="aspect-[460/300] rounded-2xl shimmer bg-[#0c1729]" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="glass rounded-2xl p-12 text-center">
            <div className="text-slate-400">لا توجد ألعاب تطابق البحث</div>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {filtered.map((g) => <GameCard key={g.id} game={g} />)}
          </div>
        )}
      </section>

      <Footer />
    </div>
  );
}

function Stat({ label, value, accent = "#e5b558" }) {
  return (
    <div className="glass rounded-xl px-4 py-2.5 flex items-center gap-2">
      <div className="text-xl font-bold" style={{ color: accent }}>{value}</div>
      <div className="text-xs text-slate-400">{label}</div>
    </div>
  );
}
function Row({ label, children }) {
  return (
    <div>
      <div className="text-[11px] text-slate-500 mb-1.5">{label}</div>
      <div className="flex flex-wrap gap-2">{children}</div>
    </div>
  );
}
function FilterPill({ active, onClick, children, testid }) {
  return (
    <button
      onClick={onClick}
      data-testid={testid}
      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition border ${
        active
          ? "bg-[rgba(229,181,88,0.15)] border-[#e5b558]/40 text-[#f4d57d]"
          : "bg-[#0c1729] border-[rgba(229,181,88,0.1)] text-slate-400 hover:text-white hover:border-[rgba(229,181,88,0.3)]"
      }`}
    >
      {children}
    </button>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-[rgba(229,181,88,0.15)] py-8 text-center">
      <div className="ornament max-w-md mx-auto mb-3">
        <Sparkles size={14} />
      </div>
      <div className="text-xs text-slate-500">© 2026 DrawCrack — مكتبة أسطورية للألعاب</div>
    </footer>
  );
}
