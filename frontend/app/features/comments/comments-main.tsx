import CommentsSkeleton from "./comments-skeleton";
import CommentsCrud from "./comments-crud";


const CommentsMain = () => {
  return ( 
    <div className="w-full py-10">
      <h1 className="text-lg font-semibold md:text-2xl mb-6">Gestionar quejas</h1>
      {/* <CommentsSkeleton /> */}
      <CommentsCrud />
    </div>

   );
}
 
export default CommentsMain;