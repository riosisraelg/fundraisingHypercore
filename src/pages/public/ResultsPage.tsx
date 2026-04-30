import { useEffect, useState } from "react";
import "./ResultsPage.css";

interface DrawResultPublic {
  folio: string;
  prize_rank: number;
  prize_name: string;
}

const RANK_EMOJI: Record<number, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };
const RANK_LABEL: Record<number, string> = {
  1: "1er Lugar",
  2: "2do Lugar",
  3: "3er Lugar",
};

const DRAW_DATE = new Date("2026-04-29T19:40:00-06:00"); // April 29, 7:40 PM CST - Draw completed

function getCountdown() {
  const now = new Date();
  const diff = DRAW_DATE.getTime() - now.getTime();
  if (diff <= 0) return null;
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  return { days, hours, minutes };
}

export default function ResultsPage() {
  // Hardcoded winners - Updated April 29, 2026
  const [results] = useState<DrawResultPublic[]>([
    {
      folio: "HC-196",
      prize_rank: 1,
      prize_name: "$5,000 MXN"
    },
    {
      folio: "HC-006", 
      prize_rank: 2,
      prize_name: "JBL Flip 7"
    },
    {
      folio: "HC-020",
      prize_rank: 3, 
      prize_name: "Botella Maestro Dobel"
    }
  ]);
  const [loading] = useState(false);
  const [drawn] = useState(true); // Draw has been completed
  const [countdown, setCountdown] = useState(getCountdown());

  useEffect(() => {
    const timer = setInterval(() => setCountdown(getCountdown()), 60000);
    return () => clearInterval(timer);
  }, []);

  // Commented out API call - using hardcoded results
  // useEffect(() => {
  //   api
  //     .get<DrawResultsResponse>("/draw/results")
  //     .then((data) => {
  //       setResults(data.results);
  //       setDrawn(data.results.length > 0);
  //     })
  //     .catch(() => {
  //       setResults([]);
  //       setDrawn(false);
  //     })
  //     .finally(() => setLoading(false));
  // }, []);

  return (
    <div className="results-page">
      <h1 className="page-heading">Resultados del Sorteo</h1>

      {loading ? (
        <p className="results-loading">Cargando resultados…</p>
      ) : drawn ? (
        <>
          <div className="draw-completed-banner">
            <p className="draw-date">🎉 Sorteo realizado el 29 de Abril, 2026 — 7:40 PM</p>
          </div>
          <div className="results-list">
            {results
              .sort((a, b) => a.prize_rank - b.prize_rank)
              .map((r) => (
                <article key={r.folio} className="result-card card-elevated">
                  <span className="result-emoji" role="img" aria-label={RANK_LABEL[r.prize_rank]}>
                    {RANK_EMOJI[r.prize_rank] ?? "🏆"}
                  </span>
                  <span className="result-rank">{RANK_LABEL[r.prize_rank]}</span>
                  <span className="result-folio">{r.folio}</span>
                  <span className="result-prize">{r.prize_name}</span>
                </article>
              ))}
          </div>
          <p className="results-note">
            Si tu folio aparece aquí, ¡felicidades! Contáctanos por WhatsApp
            para reclamar tu premio.
          </p>
        </>
      ) : (
        <div className="results-empty">
          <p className="results-date">📅 25 de Abril, 2026 — 6:00 PM</p>
          {countdown && (
            <div className="countdown">
              <div className="countdown-block">
                <span className="countdown-value">{countdown.days}</span>
                <span className="countdown-label">días</span>
              </div>
              <div className="countdown-block">
                <span className="countdown-value">{countdown.hours}</span>
                <span className="countdown-label">horas</span>
              </div>
              <div className="countdown-block">
                <span className="countdown-value">{countdown.minutes}</span>
                <span className="countdown-label">min</span>
              </div>
            </div>
          )}
          <p className="results-empty-text">
            El sorteo aún no se ha realizado. ¡Mantente atento!
          </p>
        </div>
      )}
    </div>
  );
}
