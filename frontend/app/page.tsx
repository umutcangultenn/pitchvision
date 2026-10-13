import { redirect } from "next/navigation";

/**
 * MVP: Kimlik doğrulama olmadan doğrudan panele yönlendirme.
 * Oturum / cookie tabanlı auth eklendiğinde burada login’e yönlendirme yapılabilir.
 */
export default function HomePage() {
  redirect("/dashboard");
}
