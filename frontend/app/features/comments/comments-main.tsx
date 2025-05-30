import CommentsCrud from "./comments-crud";


const CommentsMain = () => {
  return ( 
    <div className="w-full py-10 space-y-4">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Gestion de Opiniones</h1>
        <p className="text-muted-foreground">Gestion de las Opiniones y su información</p>
      </div>
      {/* <CommentsSkeleton /> */}
      <CommentsCrud />
    </div>

   );
}
 
export default CommentsMain;