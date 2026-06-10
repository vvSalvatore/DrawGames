import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api, { SOURCE_STYLES, ratingColor } from "../lib/api";
import Navbar from "../components/Navbar";
import { Footer } from "./Home";
import {
  ArrowRight, Download, Users, Wifi, HardDrive, Calendar, Tag, Star, ExternalLink,
  BookOpen, AlertTriangle, ShieldCheck, Lock, Trophy, Clock as ClockIcon
} from "lucide-react";

export default function GameDetail() {
  const { id } = useParams();
  const [game, setGame] = useState(null);
  const [tab, setTab] = useState("overview");
  const [activeShot, setActiveShot] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/games/${id}`).then((r) => { setGame(r.data); setLoading(false); }).catch(()=>setLoading(false));
  }, [id]);

  if (loading) return <div className="min-h-screen flex items-center justify-center" dir="rtl"><div className="text-slate-400">جاري التحميل...</div></div>;
  if (!game) return (
    <div dir="rtl" className="min-h-screen">
      <Navbar />
      <div className="max-w-3xl mx-auto px-6 py-20 text-center">
        <h2 className="text-3xl font-bold mb-3">لعبة غير موجودة</h2>
        <Link to="/" className="text-[#e5b558] hover:text-[#f4d57d]">العودة للمكتبة ←</Link>
      </div>
    </div>
  );

  const src = SOURCE_STYLES[game.source] || SOURCE_STYLES.fitgirl;
  const shots = game.screenshots?.length ? game.screenshots : (game.image ? [game.image, game.image] : []);
  const heroBg = game.background || game.image;
  const steamUrl = game.steam_app_id ? `https://store.steampowered.com/app/${game.steam_app_id}` : null;

  return (
    <div dir="rtl" className="min-h-screen">
      <Navbar />

      {/* Hero with background */}
      <div className="relative">
        {heroBg && (
          <div className="absolute inset-0 overflow-hidden h-[480px]">
            <img src={heroBg} alt="" className="w-full h-full object-cover opacity-30" />
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#050810]/80 to-[#050810]" />
          </div>
        )}
        <div className="relative max-w-7xl mx-auto px-6 pt-8">
          <Link to="/" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6" data-testid="back-link">
            <ArrowRight size={16} /> العودة للمكتبة
          </Link>

          <div className="grid lg:grid-cols-[1fr,360px] gap-6">
            {/* LEFT: details */}
            <div>
              {/* Cover */}
              <div className="aspect-[460/215] rounded-2xl overflow-hidden glass mb-5">
                {game.image ? <img src={game.image} alt={game.title} className="w-full h-full object-cover" /> : <div className="shimmer w-full h-full" />}
              </div>

              {/* Title */}
              <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
                <div>
                  <h1 className="heading-ar text-3xl sm:text-4xl mb-2" data-testid="game-title">{game.title}</h1>
                  <div className="flex flex-wrap gap-2 items-center text-xs">
                    {game.is_coming_soon ? (
                      <span className="coming-tag px-2.5 py-1 rounded-full">قادمة قريباً</span>
                    ) : (
                      <span className="cracked-tag px-2.5 py-1 rounded-full">مكركة جاهزة</span>
                    )}
                    <span className="px-2.5 py-1 rounded-full font-bold" style={{ background: src.bg, color: src.color, border: `1px solid ${src.border}` }}>
                      {src.name}
                    </span>
                    {game.is_coop && <span className="px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1"><Users size={12}/> تعاوني {game.coop_count > 1 ? `(${game.coop_count} لاعبين)` : ""}</span>}
                    {game.is_multiplayer && !game.is_coop && <span className="px-2.5 py-1 rounded-full bg-blue-500/15 text-blue-300 border border-blue-500/30 flex items-center gap-1"><Wifi size={12}/> متعدد</span>}
                  </div>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex gap-1 mb-5 border-b border-[rgba(229,181,88,0.2)] overflow-x-auto">
                {[
                  {k:"overview", label:"النظرة العامة"},
                  {k:"steam", label:"بيانات Steam"},
                  {k:"screenshots", label:"الصور"},
                  {k:"download", label:"التحميل والشرح"},
                ].map((t)=>(
                  <button key={t.k} onClick={()=>setTab(t.k)}
                    data-testid={`tab-${t.k}`}
                    className={`px-4 py-3 text-sm font-bold border-b-2 transition ${tab===t.k ? "tab-active" : "border-transparent text-slate-400 hover:text-white"}`}>
                    {t.label}
                  </button>
                ))}
              </div>

              {tab === "overview" && (
                <div className="space-y-5 fade-in">
                  <div className="glass rounded-2xl p-5">
                    <h3 className="heading-ar text-lg mb-3">عن اللعبة</h3>
                    <p className="text-slate-300 text-sm leading-relaxed">{game.description || "لا يوجد وصف متاح."}</p>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <InfoTile icon={HardDrive} label="الحجم" value={game.size || "—"} />
                    <InfoTile icon={Calendar} label="السنة" value={game.year || "—"} />
                    <InfoTile icon={Users} label="اللاعبين" value={game.coop_count > 1 ? `حتى ${game.coop_count}` : "1"} />
                    <InfoTile icon={Tag} label="النوع" value={game.genres?.[0] || "Action"} />
                  </div>
                  {game.genres?.length > 0 && (
                    <div className="glass rounded-2xl p-5">
                      <div className="text-xs text-slate-400 mb-3">التصنيفات</div>
                      <div className="flex flex-wrap gap-2">
                        {game.genres.map((g)=>(
                          <span key={g} className="px-2.5 py-1 rounded-lg text-xs bg-[#0c1729] border border-[rgba(229,181,88,0.15)] text-slate-300">{g}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {tab === "steam" && (
                <div className="fade-in">
                  <div className="glass-gold rounded-2xl overflow-hidden">
                    <div className="bg-gradient-to-r from-[#1b2838] to-[#0c1729] p-5 border-b border-[rgba(102,192,244,0.2)]">
                      <div className="flex items-center gap-3 mb-1">
                        <div className="w-8 h-8 rounded bg-[#171a21] flex items-center justify-center text-[#66c0f4] font-black">S</div>
                        <div className="font-bold text-[#66c0f4]" style={{fontFamily:'Cinzel'}}>Steam Store Data</div>
                      </div>
                      <div className="text-xs text-slate-400">بيانات حقيقية مأخوذة من متجر Steam مباشرة</div>
                    </div>
                    <div className="p-5 space-y-4">
                      <SteamRow icon={Star} label="تقييم Steam" value={game.steam_rating || "غير متوفر"} valueClass={ratingColor(game.steam_rating)} />
                      <SteamRow icon={Trophy} label="نسبة التقييم" value={game.steam_score ? `${game.steam_score}/100` : "—"} />
                      <SteamRow icon={Tag} label="السعر الحالي" value={game.steam_price || "—"} valueClass="text-emerald-400 font-bold" />
                      {game.steam_discount > 0 && (
                        <SteamRow icon={Tag} label="الخصم" value={`-${game.steam_discount}%`} valueClass="text-red-400 font-bold" />
                      )}
                      <SteamRow icon={Calendar} label="تاريخ الإصدار" value={game.release_date || "—"} />
                      <SteamRow icon={ClockIcon} label="حالة الإصدار" value={game.is_coming_soon ? "قادمة قريباً" : "مُصدرة"} />
                    </div>
                    {steamUrl && (
                      <a href={steamUrl} target="_blank" rel="noreferrer"
                        className="block bg-gradient-to-r from-[#1b2838] to-[#2a475e] hover:from-[#2a475e] hover:to-[#1b2838] px-5 py-3 text-center text-[#66c0f4] font-bold text-sm transition border-t border-[rgba(102,192,244,0.2)]"
                        data-testid="open-steam-btn"
                      >
                        فتح صفحة اللعبة على Steam ↗
                      </a>
                    )}
                  </div>
                </div>
              )}

              {tab === "screenshots" && (
                <div className="fade-in">
                  {shots.length === 0 ? (
                    <div className="glass rounded-2xl p-10 text-center text-slate-400">لا توجد صور متاحة بعد</div>
                  ) : (
                    <>
                      <div className="aspect-video rounded-2xl overflow-hidden mb-3 glass">
                        <img src={shots[activeShot]} alt="" className="w-full h-full object-cover" />
                      </div>
                      <div className="grid grid-cols-4 gap-2">
                        {shots.slice(0,6).map((s,i)=>(
                          <button key={`${s}-${i}`} onClick={()=>setActiveShot(i)}
                            className={`aspect-video rounded-lg overflow-hidden border-2 transition ${activeShot===i?"border-[#e5b558]":"border-transparent opacity-60 hover:opacity-100"}`}>
                            <img src={s} alt="" className="w-full h-full object-cover" />
                          </button>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              )}

              {tab === "download" && <DownloadGuide game={game} src={src} />}
            </div>

            {/* RIGHT: action panel */}
            <aside className="lg:sticky lg:top-24 self-start space-y-4">
              <div className="glass-gold rounded-2xl p-5">
                <div className="text-xs text-slate-400 mb-2">المصدر</div>
                <div className="text-lg font-bold mb-4" style={{color: src.color}}>{src.name}</div>

                {game.is_coming_soon ? (
                  <button disabled className="w-full py-3.5 rounded-xl bg-red-900/30 border border-red-900/40 text-red-300 font-bold flex items-center justify-center gap-2" data-testid="download-disabled">
                    <ClockIcon size={16}/> لم تُطلق بعد
                  </button>
                ) : game.torrent_url ? (
                  game.torrent_url.startsWith("magnet:") ? (
                    <a href={game.torrent_url} className="btn-legendary w-full py-3.5 rounded-xl flex items-center justify-center gap-2" data-testid="download-torrent-btn">
                      <Download size={16}/> فتح Magnet للتحميل
                    </a>
                  ) : (
                    <a href={game.torrent_url} target="_blank" rel="noreferrer" className="btn-legendary w-full py-3.5 rounded-xl flex items-center justify-center gap-2" data-testid="download-torrent-btn">
                      <ExternalLink size={16}/> صفحة التحميل
                    </a>
                  )
                ) : (
                  <FindTorrentButton gameId={game.id} onFound={(d)=>setGame({...game, torrent_url: d.torrent_url, source: d.source, archive_password: d.source==='online-fix'?'online-fix.me':game.archive_password})} />
                )}

                <div className="mt-4 pt-4 border-t border-[rgba(229,181,88,0.15)] space-y-2 text-xs">
                  <Mini label="الحجم" value={game.size} />
                  <Mini label="السنة" value={game.year} />
                  {game.archive_password && (
                    <div className="flex items-center justify-between gap-2 p-2 rounded-lg bg-blue-500/10 border border-blue-500/30">
                      <span className="text-blue-300 flex items-center gap-1.5"><Lock size={12}/> كلمة سر الضغط</span>
                      <span className="font-mono text-blue-200">{game.archive_password}</span>
                    </div>
                  )}
                </div>

                <Link to={`/sources/${game.source}`} className="mt-4 block text-center text-xs text-[#e5b558] hover:text-[#f4d57d]" data-testid="view-tutorial-link">
                  <BookOpen size={12} className="inline ml-1" /> شرح التثبيت لـ {src.name}
                </Link>
              </div>

              {steamUrl && (
                <a href={steamUrl} target="_blank" rel="noreferrer"
                  className="block glass rounded-2xl p-4 hover:border-[#66c0f4]/40 transition text-center text-sm text-[#66c0f4] font-bold">
                  ↗ ادعم المطور — فتح في Steam
                </a>
              )}
            </aside>
          </div>
        </div>
      </div>

      <div className="h-16" />
      <Footer />
    </div>
  );
}

function InfoTile({ icon: I, label, value }) {
  return (
    <div className="glass rounded-xl p-3 text-center">
      <I size={14} className="text-[#e5b558] mx-auto mb-1.5" />
      <div className="text-[10px] text-slate-500 mb-0.5">{label}</div>
      <div className="text-sm font-bold">{value}</div>
    </div>
  );
}

function SteamRow({ icon: I, label, value, valueClass = "" }) {
  return (
    <div className="flex items-center justify-between border-b border-[rgba(102,192,244,0.1)] pb-3 last:border-0 last:pb-0">
      <div className="flex items-center gap-2 text-sm text-slate-400">
        <I size={14} className="text-[#66c0f4]" /> {label}
      </div>
      <div className={`text-sm font-bold ${valueClass}`}>{value}</div>
    </div>
  );
}

function Mini({ label, value }) {
  return (
    <div className="flex items-center justify-between text-slate-400">
      <span>{label}</span>
      <span className="text-slate-200 font-bold">{value || "—"}</span>
    </div>
  );
}

function FindTorrentButton({ gameId, onFound }) {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const find = async () => {
    setLoading(true); setErr("");
    try {
      const { data } = await api.post(`/games/${gameId}/find-torrent`);
      onFound(data);
    } catch (e) {
      setErr(e.response?.data?.detail || "تعذر البحث");
    } finally { setLoading(false); }
  };
  return (
    <div>
      <button onClick={find} disabled={loading} className="btn-legendary w-full py-3.5 rounded-xl flex items-center justify-center gap-2" data-testid="find-torrent-btn">
        {loading ? <><span className="animate-spin">⟳</span> جاري البحث في 4 مصادر...</> : <>🔍 ابحث عن تورنت تلقائياً</>}
      </button>
      {err && <div className="mt-2 text-xs text-red-400 bg-red-500/10 border border-red-500/30 px-3 py-2 rounded-lg">{err}</div>}
      <div className="mt-2 text-[11px] text-slate-500 text-center">يبحث في FitGirl + Online-Fix + AnkerGames + SteamUnlocked</div>
    </div>
  );
}

function DownloadGuide({ game, src }) {
  const [source, setSource] = useState(null);
  useEffect(()=>{ api.get(`/sources/${game.source}`).then(r=>setSource(r.data)); }, [game.source]);

  return (
    <div className="fade-in space-y-4">
      <div className="glass-gold rounded-2xl p-5 border-r-4" style={{borderRightColor: src.color}}>
        <div className="flex items-start gap-3">
          <ShieldCheck size={20} className="text-[#e5b558] mt-1" />
          <div>
            <div className="font-bold mb-1">دليل التحميل من {src.name}</div>
            <div className="text-xs text-slate-400">اتبع الخطوات بالترتيب لتثبيت اللعبة بدون أخطاء.</div>
          </div>
        </div>
      </div>

      {!source ? (
        <div className="glass rounded-2xl p-10 text-center text-slate-400">جاري تحميل الشرح...</div>
      ) : (
        <>
          {source.archive_password && (
            <div className="glass rounded-2xl p-4 border-r-4 border-blue-500 flex items-center gap-3">
              <Lock className="text-blue-400" size={18} />
              <div className="flex-1">
                <div className="font-bold text-sm">كلمة سر ملفات الضغط</div>
                <div className="text-xs text-slate-400">احفظها — ستحتاجها عند فك الضغط</div>
              </div>
              <code className="bg-blue-500/15 text-blue-300 px-3 py-1.5 rounded-lg font-mono text-sm">{source.archive_password}</code>
            </div>
          )}

          <ol className="space-y-3">
            {source.steps_ar.map((s, i)=>(
              <li key={s.title} className="glass rounded-2xl p-5 flex gap-4">
                <div className="shrink-0 w-9 h-9 rounded-full bg-gradient-to-br from-[#f4d57d] to-[#a07a26] text-[#1a1207] font-black flex items-center justify-center" style={{fontFamily:'Cinzel'}}>{i+1}</div>
                <div className="flex-1">
                  <div className="font-bold mb-1.5">{s.title}</div>
                  <div className="text-sm text-slate-400 leading-relaxed">{s.body}</div>
                </div>
              </li>
            ))}
          </ol>

          {source.tips_ar?.length > 0 && (
            <div className="glass rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle size={16} className="text-amber-400" />
                <div className="font-bold">نصائح مهمة</div>
              </div>
              <ul className="space-y-2 text-sm text-slate-300">
                {source.tips_ar.map((t)=>(
                  <li key={t} className="flex gap-2"><span className="text-amber-400">▸</span> {t}</li>
                ))}
              </ul>
            </div>
          )}

          <a href={source.url} target="_blank" rel="noreferrer"
            className="btn-legendary w-full py-3.5 rounded-xl flex items-center justify-center gap-2"
            data-testid="open-source-site-btn"
          >
            افتح موقع {source.name} للتحميل <ExternalLink size={16}/>
          </a>
        </>
      )}
    </div>
  );
}
