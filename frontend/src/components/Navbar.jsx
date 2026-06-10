import { Link, NavLink, useLocation } from "react-router-dom";
import { Library, Clock, BookOpen, Home, Search } from "lucide-react";

export default function Navbar() {
  const loc = useLocation();
  const link = ({ isActive }) =>
    `relative px-4 py-2 text-sm font-bold transition-colors ${
      isActive ? "text-[#f4d57d]" : "text-slate-300 hover:text-white"
    }`;

  return (
    <header className="sticky top-0 z-50 glass border-b border-[rgba(229,181,88,0.18)]">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3" data-testid="logo-link">
          <div className="relative w-11 h-11 rounded-xl bg-gradient-to-br from-[#f4d57d] via-[#e5b558] to-[#a07a26] flex items-center justify-center font-black text-[#1a1207] text-xl shadow-[0_4px_20px_-6px_rgba(229,181,88,0.5)]">
            ✦
          </div>
          <div>
            <div className="font-bold text-lg leading-tight" style={{fontFamily:'Cinzel, serif'}}>DrawCrack</div>
            <div className="text-[10px] text-[#e5b558] tracking-widest">LEGENDARY LIBRARY</div>
          </div>
        </Link>
        <nav className="hidden md:flex items-center gap-1">
          <NavLink to="/" end className={link} data-testid="nav-home"><span className="flex items-center gap-2"><Home size={14}/> الرئيسية</span></NavLink>
          <NavLink to="/library" className={link} data-testid="nav-library"><span className="flex items-center gap-2"><Library size={14}/> المكتبة</span></NavLink>
          <NavLink to="/coming-soon" className={link} data-testid="nav-coming"><span className="flex items-center gap-2"><Clock size={14}/> قادمة</span></NavLink>
          <NavLink to="/sources" className={link} data-testid="nav-sources"><span className="flex items-center gap-2"><BookOpen size={14}/> دليل المصادر</span></NavLink>
        </nav>
      </div>
    </header>
  );
}
