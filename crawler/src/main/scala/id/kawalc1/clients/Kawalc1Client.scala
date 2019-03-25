package id.kawalc1.clients

import akka.actor.ActorSystem
import akka.http.scaladsl.client.RequestBuilding._
import akka.stream.Materializer

import scala.concurrent.Future

class Kawalc1Client(baseUrl: String)(implicit val system: ActorSystem, val mat: Materializer) extends HttpClientSupport with JsonSupport {

  def getKelurahan(number: Long): Future[Either[String, Kelurahan]] = execute[Kelurahan](Get(s"$baseUrl/$number"))

}
