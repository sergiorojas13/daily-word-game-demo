import { useCallback, useEffect, useMemo, useRef, useState } from "react";

type Traza = {
  val_orden: number;
  cod_termino: string;
  txt_patron: string;
  detalle: string[];
};

type UserStateResponse = {
  status: string;
  data?: {
    pk_cuaderno: number;
    pk_bitacora?: number;
    td_referencia: string;
    cod_usuario: string;
    des_usuario?: string | null;
    flg_existe_bitacora: boolean;
    flg_resuelto: boolean;
    flg_cerrado: boolean;
    val_intento_ok?: number | null;
    val_intento_total: number;
    val_puntos: number;
    val_longitud: number;
    val_max_intentos: number;
    trazas: Traza[];
  };
  message?: string;
};

type AttemptSubmitResponse = {
  status: string;
  data?: {
    message?: string;
    flg_registrado?: boolean;
    flg_valido?: boolean;
    flg_acierto?: boolean;
    flg_cerrado?: boolean;
  };
};

const STORAGE_DEVICE_KEY = "mente_device_id";

function normalizeLetter(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/ñ/gi, "n")
    .toLowerCase();
}

function sanitizeGuess(value: string, maxLength: number): string {
  return normalizeLetter(value).replace(/[^a-z]/g, "").slice(0, maxLength);
}

function buildDeviceId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `dv_${crypto.randomUUID().replace(/-/g, "")}`;
  }

  return `dv_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

function getOrCreateDeviceId(): string {
  const current = window.localStorage.getItem(STORAGE_DEVICE_KEY);
  if (current && current.trim().length > 0) {
    return current.trim();
  }

  const next = buildDeviceId();
  window.localStorage.setItem(STORAGE_DEVICE_KEY, next);
  return next;
}

function getStatusClass(message: string): string {
  const text = message.toLowerCase();

  if (text.includes("correcto") || text.includes("registrado")) {
    return "status-card status-card--success";
  }

  if (
    text.includes("error") ||
    text.includes("http") ||
    text.includes("no se pudo") ||
    text.includes("no registrado")
  ) {
    return "status-card status-card--error";
  }

  return "status-card status-card--info";
}

function formatCountdown(totalSeconds: number): string {
  const safeSeconds = Math.max(0, totalSeconds);
  const hours = Math.floor(safeSeconds / 3600);
  const minutes = Math.floor((safeSeconds % 3600) / 60);
  const seconds = safeSeconds % 60;

  return [hours, minutes, seconds]
    .map((value) => String(value).padStart(2, "0"))
    .join(":");
}

export default function App() {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const [deviceId, setDeviceId] = useState<string>("");
  const [identityReady, setIdentityReady] = useState<boolean>(false);

  const [state, setState] = useState<UserStateResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [currentGuess, setCurrentGuess] = useState<string>("");
  const [message, setMessage] = useState<string>("");
  const [countdown, setCountdown] = useState<string>("--:--:--");

  useEffect(() => {
    const id = getOrCreateDeviceId();
    setDeviceId(id);
    setIdentityReady(true);
  }, []);

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      const next = new Date(now);
      next.setHours(24, 0, 0, 0);

      const seconds = Math.floor((next.getTime() - now.getTime()) / 1000);
      setCountdown(formatCountdown(seconds));
    };

    tick();
    const timerId = window.setInterval(tick, 1000);

    return () => window.clearInterval(timerId);
  }, []);

  const loadUserState = useCallback(async (codUsuario: string) => {
    const response = await fetch("/mente-api/user-day-state", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        cod_usuario: codUsuario
      }),
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const json = (await response.json()) as UserStateResponse;
    setState(json);
    return json;
  }, []);

  useEffect(() => {
    if (!identityReady || !deviceId) {
      return;
    }

    const run = async () => {
      try {
        setLoading(true);
        setMessage("");
        await loadUserState(deviceId);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Error al cargar estado";
        setMessage(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    void run();
  }, [identityReady, deviceId, loadUserState]);

  const gameData = state?.data;
  const longitud = gameData?.val_longitud ?? 5;
  const maxIntentos = gameData?.val_max_intentos ?? 6;
  const trazas = gameData?.trazas ?? [];
  const flgCerrado = gameData?.flg_cerrado ?? false;
  const flgResuelto = gameData?.flg_resuelto ?? false;

  useEffect(() => {
    if (!loading && !flgCerrado) {
      inputRef.current?.focus();
    }
  }, [loading, flgCerrado]);

  const estadoPartida = useMemo(() => {
    if (!flgCerrado) {
      return {
        className: "state-banner state-banner--ready",
        title: "Palabra del día disponible",
        subtitle: `Tienes ${maxIntentos} intentos para resolverla.`
      };
    }

    if (flgResuelto) {
      return {
        className: "state-banner state-banner--success",
        title: "Muy bien. La has resuelto",
        subtitle: `La siguiente palabra estará disponible en ${countdown}.`
      };
    }

    return {
      className: "state-banner state-banner--closed",
      title: "Ronda terminada",
      subtitle: `La siguiente palabra estará disponible en ${countdown}.`
    };
  }, [flgCerrado, flgResuelto, maxIntentos, countdown]);

  const filas = useMemo(() => {
    return Array.from({ length: maxIntentos }, (_, rowIndex) => {
      const traza = trazas[rowIndex];

      if (traza) {
        return traza.cod_termino.split("").map((letra, idx) => ({
          letra,
          estado: traza.detalle[idx] ?? "empty"
        }));
      }

      const isCurrentRow = rowIndex === trazas.length && !flgCerrado;
      if (isCurrentRow) {
        return Array.from({ length: longitud }, (_, colIndex) => ({
          letra: currentGuess[colIndex] ?? "",
          estado: "empty"
        }));
      }

      return Array.from({ length: longitud }, () => ({
        letra: "",
        estado: "empty"
      }));
    });
  }, [trazas, currentGuess, flgCerrado, longitud, maxIntentos]);

  const submitGuess = useCallback(async () => {
    if (!gameData || flgCerrado || submitting || !deviceId) {
      return;
    }

    const guess = sanitizeGuess(currentGuess.trim(), longitud);

    if (guess.length !== longitud) {
      setMessage(`La palabra debe tener ${longitud} letras.`);
      return;
    }

    try {
      setSubmitting(true);
      setMessage("");

      const response = await fetch("/mente-api/attempt-submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          cod_usuario: deviceId,
          des_usuario: null,
          cod_termino: guess
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = (await response.json()) as AttemptSubmitResponse;

      if (result.status !== "ok") {
        setMessage(result.data?.message ?? "No se pudo registrar el intento.");
        return;
      }

      if (result.data?.flg_registrado === false) {
        setMessage(result.data?.message ?? "Intento no registrado.");
        return;
      }

      if (result.data?.flg_acierto) {
        setMessage("Correcto. Has resuelto la palabra de hoy.");
      } else {
        setMessage("");
      }

      setCurrentGuess("");
      await loadUserState(deviceId);
      inputRef.current?.focus();
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Error al enviar intento";
      setMessage(errorMessage);
    } finally {
      setSubmitting(false);
    }
  }, [currentGuess, deviceId, flgCerrado, gameData, loadUserState, longitud, submitting]);

  const handleGuessChange = (value: string) => {
    if (loading || submitting || flgCerrado) {
      return;
    }

    setCurrentGuess(sanitizeGuess(value, longitud));
  };

  const handleGuessKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      event.preventDefault();
      void submitGuess();
    }
  };

  if (loading) {
    return (
      <div className="app-shell">
        <div className="panel">
          <div className="panel__eyebrow">Pausa breve</div>
          <div className="panel__header">
            <div>
              <h1>Ejercita tu mente</h1>
              <p>Una palabra al día. Un momento para desconectar.</p>
            </div>
          </div>

          <div className="status-card status-card--info">Cargando...</div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="app-shell"
      onClick={() => {
        if (!flgCerrado) {
          inputRef.current?.focus();
        }
      }}
    >
      <div className="panel">
        <input
          ref={inputRef}
          type="text"
          value={currentGuess}
          onChange={(e) => handleGuessChange(e.target.value)}
          onKeyDown={handleGuessKeyDown}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="none"
          spellCheck={false}
          disabled={flgCerrado || submitting}
          style={{
            position: "absolute",
            opacity: 0,
            pointerEvents: "none",
            width: 1,
            height: 1
          }}
        />

        <div className="panel__eyebrow">Pausa breve</div>

        <div className="panel__header">
          <div>
            <h1>Ejercita tu mente</h1>
            <p>Una palabra al día. Un momento para desconectar.</p>
          </div>

          <div className="panel__badge">
            <span className="panel__badge-label">Hoy</span>
            <strong>{gameData?.td_referencia ?? "-"}</strong>
          </div>
        </div>

        <div className={estadoPartida.className}>
          <strong>{estadoPartida.title}</strong>
          <span>{estadoPartida.subtitle}</span>
        </div>

        <div className="board-wrap">
          <div className="board">
            {filas.map((fila, i) => (
              <div key={i} className="row">
                {fila.map((celda, j) => (
                  <div key={j} className={`cell cell--${celda.estado}`}>
                    {celda.letra}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        <div className="game-meta">
          <div className="meta-card">
            <span className="meta-card__label">Intentos</span>
            <strong>{trazas.length} / {maxIntentos}</strong>
          </div>

          <div className="meta-card">
            <span className="meta-card__label">Puntos</span>
            <strong>{gameData?.val_puntos ?? 0}</strong>
          </div>
        </div>

        {message ? <div className={getStatusClass(message)}>{message}</div> : null}

        {!flgCerrado ? (
          <div className="helper-text">
            Pulsa sobre la pantalla y escribe. Enter para enviar, Backspace para borrar.
          </div>
        ) : (
          <div className="helper-text helper-text--closed">
            La ronda de hoy ya está cerrada.
          </div>
        )}

        <div className="legend">
          <div className="legend__title">Cómo funciona</div>

          <div className="legend__grid">
            <div className="legend__item">
              <span className="legend__swatch legend__swatch--V">V</span>
              <span>Letra correcta en la posición correcta.</span>
            </div>

            <div className="legend__item">
              <span className="legend__swatch legend__swatch--N">N</span>
              <span>La letra está, pero en otra posición.</span>
            </div>

            <div className="legend__item">
              <span className="legend__swatch legend__swatch--G">G</span>
              <span>La letra no aparece en la palabra.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
