import { Link } from "react-router-dom";
import { SOURCE_STYLES } from "../lib/api";
import { Users, Wifi, Star } from "lucide-react";

export default function GameCard({ game }) {
  const src = SOURCE_STYLES[game.source] || SOURCE_STYLES.fitgirl;
  const isComing = game.is_coming_soon;
  const score = game.steam_score;

  return (
    <Link
      to={`/game/${game.id}`}
      className="group glass card-lift rounded-2xl overflow-hidden flex flex-col"
      data-testid={`game-card-${game.id}`}
    >
      <div className="relative aspect-[460/215] bg-[#0c1729] overflow-hidden">
        {game.image ? (
          <img src={game.image} alt={game.title} loading="lazy"
            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
        ) : (
          <div className="w-full h-full shimmer" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />

        <div className="absolute top-3 right-3 flex gap-1.5">
          {isComing ? (
            <span className="coming-tag text-[10px] px-2 py-1 rounded-full" data-testid={`tag-coming-${game.id}`}>قادمة قريباً</span>
          ) : (
            <span className="cracked-tag text-[10px] px-2 py-1 rounded-full" data-testid={`tag-cracked-${game.id}`}>مكركة</span>
          )}
        </div>

        <div className="absolute top-3 left-3 px-2 py-1 rounded-full text-[10px] font-bold"
             style={{ background: src.bg, color: src.color, border: `1px solid ${src.border}` }}>
          {src.name}
        </div>

        {/* hover info strip */}
        <div className="absolute bottom-2 left-2 right-2 flex items-center gap-2 text-[11px] text-slate-200 opacity-0 group-hover:opacity-100 transition">
          {game.year && game.year !== "—" && <span>{game.year}</span>}
          {game.size && <span>·  {game.size}</span>}
        </div>
      </div>

      <div className="p-4 flex-1 flex flex-col">
        <h3 className="font-bold text-base text-white group-hover:text-[#f4d57d] transition-colors line-clamp-2 mb-2" data-testid={`game-title-${game.id}`}>
          {game.title}
        </h3>
        <div className="flex items-center justify-between text-[11px] text-slate-400 mt-auto">
          <div className="flex items-center gap-1.5">
            {game.is_coop && <span className="flex items-center gap-1 text-emerald-400" title="Co-op"><Users size={11}/> كوب</span>}
            {!game.is_coop && game.is_multiplayer && <span className="flex items-center gap-1 text-blue-400"><Wifi size={11}/> ملتي</span>}
          </div>
          {score && (
            <div className="flex items-center gap-1 rating-pos">
              <Star size={11} fill="currentColor" /> {score}
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
