import SigninForm from "~/features/signin/signin-form"

export default function Signin() {
  return (
    <main className="w-full min-h-screen flex justify-center items-center p-8">
      <div className="flex flex-col items-center gap-4 p-8 border border-neutral-300 rounded-lg">
        <h1 className="text-4xl font-bold">Acceso</h1>
        <SigninForm />
      </div>
    </main>
  )
}