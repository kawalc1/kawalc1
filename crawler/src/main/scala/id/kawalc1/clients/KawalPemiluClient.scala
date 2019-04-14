package id.kawalc1.clients

import akka.actor.ActorSystem
import akka.http.scaladsl.client.RequestBuilding._
import akka.stream.Materializer
import id.kawalc1.Kelurahan

import scala.concurrent.Future

class KawalPemiluClient(baseUrl: String)(implicit val system: ActorSystem, val mat: Materializer)
  extends HttpClientSupport
  with JsonSupport {

  def getKelurahan(number: Long): Future[Either[Response, Kelurahan]] =
    execute[Kelurahan](Get(s"$baseUrl/$number"))

}
