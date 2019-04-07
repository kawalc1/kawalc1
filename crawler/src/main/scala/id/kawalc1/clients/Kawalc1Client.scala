package id.kawalc1.clients

import akka.actor.ActorSystem
import akka.http.scaladsl.client.RequestBuilding._
import akka.http.scaladsl.model.Uri
import akka.http.scaladsl.model.Uri.Query
import akka.stream.Materializer

import scala.concurrent.Future

case class Transform(
  transformedUrl: Option[String],
  transformedUri: Option[String],
  success: Boolean)

case class Extracted(
  probabilities: Seq[Double],
  filename: String)

case class Numbers(
  id: String,
  shortName: String,
  displayName: String,
  extracted: Seq[Extracted])

case class Extraction(
  numbers: Seq[Numbers],
  digitArea: String)

class KawalC1Client(baseUrl: String)(implicit val system: ActorSystem, val mat: Materializer)
  extends HttpClientSupport
  with JsonSupport {

  def alignPhoto(
    kelurahan: Int,
    tps: Int,
    photoUrl: String,
    quality: Int,
    formConfig: String): Future[Either[String, Transform]] = {
    val url = Uri(s"$baseUrl/align/$kelurahan/$tps/$photoUrl=s$quality")
      .withQuery(
        Query(
          "storeFiles" -> "true",
          "baseUrl" -> "http://lh3.googleusercontent.com",
          "configFile" -> formConfig))
    execute[Transform](Get(url))
  }

  def extractNumbers(
    kelurahan: Int,
    tps: Int,
    photoUrl: String,
    formConfig: String): Future[Either[String, Extraction]] = {

    val url = Uri(s"$baseUrl/extract/$kelurahan/$tps/$photoUrl")
      .withQuery(
        Query(
          "baseUrl" -> "https://storage.googleapis.com/kawalc1/static/transformed",
          "configFile" -> formConfig))
    execute[Extraction](Get(url))
  }

}
