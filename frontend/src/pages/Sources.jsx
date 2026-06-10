import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../lib/api";
import Navbar from "../components/Navbar";
import { Footer } from "./Home";
import { ExternalLink, Lock, AlertTriangle, ShieldCheck, ArrowRight, BookOpen } from "lucide-react";

export function SourcesList() {
  const [sources, setSources] = useState([]);
  useEffect(()=>{ api.get("/sources").then(r=>setSources(r.data)); }, []);
  return (
    <div dir="rtl" className="min-h-screen">
      <Navbar />
      <section className="max-w-7xl mx-auto px-6 pt-16 pb-20 relative">
        <div className="absolute inset-0 grid-pattern" />
        <div className="ornament mb-6"><span className="text-xs tracking-[0.3em]">★ DOWNLOAD SOURCES ★</span></div>
        <h1 className="heading-ar text-5xl sm:text-6xl text-center mb-4">
          دليل <span className="gold-text">المصادر</span>
        </h1>
        <p className="text-center text-slate-400 max-w-2xl mx-auto mb-12 text-sm">
          شرح تفصيلي لكل موقع تحميل: كيف تحمّل، كيف تثبّت، وأهم النصائح.
        </p>

        <div className="grid md:grid-cols-2 gap-5">
          {sources.map((s)=>(
            <Link key={s.id} to={`/sources/${s.id}`} className="glass card-lift rounded-2xl p-6 flex flex-col" style={{borderColor: 'rgba(229,181,88,0.15)'}} data-testid={`source-card-${s.id}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-black"
                     style={{background:`${s.color}22`, border:`1px solid ${s.color}66`, color: s.color}}>
                  {s.name.charAt(0)}
                </div>
                <div>
                  <div className="font-bold text-xl" style={{color: s.color}}>{s.name}</div>
                  <div className="text-xs text-slate-500">{s.url.replace("https://","")}</div>
                </div>
              </div>
              <p className="text-sm text-slate-300 mb-4 line-clamp-3 leading-relaxed">{s.desc_ar}</p>
              <ul className="space-y-1.5 text-xs text-slate-400 flex-1 mb-4">
                {s.features_ar.slice(0,3).map((f)=>(
                  <li key={f} className="flex gap-2"><span style={{color:s.color}}>◆</span> {f}</li>
                ))}
              </ul>
              <div className="flex items-center justify-between text-sm font-bold pt-3 border-t border-[rgba(229,181,88,0.1)]" style={{color:s.color}}>
                <span>اقرأ الدليل الكامل</span>
                <ArrowRight size={14} />
              </div>
            </Link>
          ))}
        </div>
      </section>
      <Footer />
    </div>
  );
}

export default function SourceDetail() {
  const { id } = useParams();
  const [s, setS] = useState(null);
  useEffect(()=>{ api.get(`/sources/${id}`).then(r=>setS(r.data)).catch(()=>setS(null)); }, [id]);

  if (!s) return <div className="min-h-screen flex items-center justify-center" dir="rtl"><div className="text-slate-400">جاري التحميل...</div></div>;

  return (
    <div dir="rtl" className="min-h-screen">
      <Navbar />
      <div className="max-w-4xl mx-auto px-6 pt-10 pb-20">
        <Link to="/sources" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6">
          <ArrowRight size={16}/> العودة لقائمة المصادر
        </Link>

        <div className="glass-gold rounded-3xl p-8 mb-6 border-r-4" style={{borderRightColor: s.color}}>
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl font-black"
              style={{background:`${s.color}22`, border:`1px solid ${s.color}66`, color: s.color}}>
              {s.name.charAt(0)}
            </div>
            <div>
              <h1 className="heading-ar text-3xl sm:text-4xl mb-1" style={{color: s.color}}>{s.name}</h1>
              <a href={s.url} target="_blank" rel="noreferrer" className="text-sm text-slate-400 hover:text-white inline-flex items-center gap-1">
                {s.url.replace("https://","")} <ExternalLink size={12}/>
              </a>
            </div>
          </div>
          <p className="text-slate-300 leading-relaxed mb-5">{s.desc_ar}</p>
          <div className="grid sm:grid-cols-2 gap-2">
            {s.features_ar.map((f)=>(
              <div key={f} className="flex items-start gap-2 text-sm text-slate-300">
                <ShieldCheck size={14} className="mt-0.5 shrink-0" style={{color: s.color}} /> {f}
              </div>
            ))}
          </div>
        </div>

        {s.archive_password && (
          <div className="glass rounded-2xl p-5 mb-6 border-r-4 border-blue-500 flex items-center gap-4">
            <Lock size={22} className="text-blue-400 shrink-0" />
            <div className="flex-1">
              <div className="font-bold mb-1">كلمة سر فك الضغط</div>
              <div className="text-xs text-slate-400">احفظها — ستحتاجها لفك ملفات هذا الموقع</div>
            </div>
            <code className="bg-blue-500/20 border border-blue-500/40 text-blue-200 px-4 py-2 rounded-xl font-mono text-base font-bold">{s.archive_password}</code>
          </div>
        )}

        <h2 className="heading-ar text-2xl mb-4 flex items-center gap-2"><BookOpen size={20} className="text-[#e5b558]"/> خطوات التثبيت</h2>
        <ol className="space-y-3 mb-8">
          {s.steps_ar.map((step,i)=>(
            <li key={step.title} className="glass rounded-2xl p-5 flex gap-4" data-testid={`step-${i}`}>
              <div className="shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-[#f4d57d] to-[#a07a26] text-[#1a1207] font-black flex items-center justify-center text-xl" style={{fontFamily:'Cinzel'}}>{i+1}</div>
              <div className="flex-1">
                <div className="font-bold mb-2 text-lg">{step.title}</div>
                <div className="text-sm text-slate-300 leading-relaxed">{step.body}</div>
              </div>
            </li>
          ))}
        </ol>

        {s.tips_ar?.length > 0 && (
          <div className="glass rounded-2xl p-5 mb-6">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle size={18} className="text-amber-400" />
              <div className="font-bold text-lg">نصائح مهمة</div>
            </div>
            <ul className="space-y-2.5 text-sm text-slate-300">
              {s.tips_ar.map((t)=>(
                <li key={t} className="flex gap-2"><span className="text-amber-400 mt-0.5">▸</span> {t}</li>
              ))}
            </ul>
          </div>
        )}

        <a href={s.url} target="_blank" rel="noreferrer" className="btn-legendary w-full py-4 rounded-xl flex items-center justify-center gap-2 text-base" data-testid="visit-source-btn">
          زيارة {s.name} الآن <ExternalLink size={16}/>
        </a>
      </div>
      <Footer />
    </div>
  );
}
