/** Modal sencillo reutilizable. */
export default function Modal({ titulo, children, onCerrar }) {
  return (
    <div className="modal" role="dialog" aria-modal="true">
      <div className="modal__panel tarjeta">
        <div className="modal__cabecera">
          <h3>{titulo}</h3>
          <button className="boton boton--secundario" onClick={onCerrar}>
            Cerrar
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
