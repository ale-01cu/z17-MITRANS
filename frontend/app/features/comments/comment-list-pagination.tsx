import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "~/components/ui/pagination";

interface Props {
  pages: number; // Número total de páginas
  showPages: number; // Número de páginas visibles en la paginación
  nextUrl: string | undefined; // URL para la página siguiente
  previousUrl: string | undefined; // URL para la página anterior
  currentPage: number; // Página actual (necesaria para resaltar la página activa)
}

const CommentListPagination = ({
  pages,
  showPages,
  nextUrl,
  previousUrl,
  currentPage,
}: Props) => {
  // Calcular el rango de páginas a mostrar
  const half = Math.floor(showPages / 2);
  let start = Math.max(currentPage - half, 1);
  let end = Math.min(start + showPages - 1, pages);

  // Ajustar el inicio si el rango excede el número total de páginas
  if (end - start + 1 < showPages) {
    start = Math.max(end - showPages + 1, 1);
  }

  // Generar un array de páginas para mostrar
  const pageNumbers = Array.from(
    { length: end - start + 1 },
    (_, i) => start + i
  );

  return (
    <Pagination>
      <PaginationContent>
        {/* Botón "Anterior" */}
        <PaginationItem>
          <PaginationPrevious
            href={currentPage > 1 ? previousUrl : "#"}
            aria-disabled={currentPage <= 1}
            className="cursor-pointer"
          />
        </PaginationItem>

        {/* Mostrar páginas */}
        {pageNumbers.map((page) => (
          <PaginationItem key={page}>
            <PaginationLink
              href={`?page=${page}`}
              isActive={page === currentPage}
            >
              {page}
            </PaginationLink>
          </PaginationItem>
        ))}

        {/* Mostrar puntos suspensivos si hay más páginas después del rango */}
        {end < pages && (
          <PaginationItem>
            <PaginationEllipsis />
          </PaginationItem>
        )}

        {/* Botón "Siguiente" */}
        <PaginationItem>
          <PaginationNext
            href={currentPage < pages ? nextUrl : "#"}
            aria-disabled={currentPage >= pages}
            className="cursor-pointer"
          />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
};

export default CommentListPagination;