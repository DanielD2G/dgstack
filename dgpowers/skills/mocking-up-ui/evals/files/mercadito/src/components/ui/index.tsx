import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from "react";
import "./ui.css";

export function Card({ title, children }: { title?: string; children: ReactNode }) {
  return (
    <section className="mk-card">
      {title && <h2 className="mk-card__title">{title}</h2>}
      {children}
    </section>
  );
}

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
  icon?: ReactNode;
};
export function Button({ variant = "primary", icon, children, ...rest }: ButtonProps) {
  return (
    <button className={`mk-btn mk-btn--${variant}`} {...rest}>
      {icon}
      {children}
    </button>
  );
}

type FieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  hint?: string;
  error?: string;
};
export function Field({ label, hint, error, id, ...rest }: FieldProps) {
  return (
    <div className="mk-field">
      <label className="mk-field__label" htmlFor={id}>{label}</label>
      <input id={id} className={`mk-input${error ? " mk-input--invalid" : ""}`} aria-invalid={!!error} {...rest} />
      {error ? <span className="mk-field__error">{error}</span> : hint && <span className="mk-field__hint">{hint}</span>}
    </div>
  );
}

export function Badge({ tone, children }: { tone: "ok" | "warn"; children: ReactNode }) {
  return <span className={`mk-badge mk-badge--${tone}`}>{children}</span>;
}

export function Switch({ on, label, onChange }: { on: boolean; label: string; onChange: (on: boolean) => void }) {
  return (
    <label className="mk-switch">
      <button type="button" role="switch" aria-checked={on} className="mk-switch__track" data-on={on} onClick={() => onChange(!on)}>
        <span className="mk-switch__thumb" />
      </button>
      {label}
    </label>
  );
}

export function RadioCard({ selected, title, detail, onSelect }: { selected: boolean; title: string; detail: string; onSelect: () => void }) {
  return (
    <div className="mk-radio-card" data-selected={selected} role="radio" aria-checked={selected} tabIndex={0} onClick={onSelect}>
      <div>
        <strong>{title}</strong>
        <div className="mk-field__hint">{detail}</div>
      </div>
    </div>
  );
}
