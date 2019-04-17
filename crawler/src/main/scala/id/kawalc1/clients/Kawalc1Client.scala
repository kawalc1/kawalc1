package id.kawalc1.clients

import akka.actor.ActorSystem
import akka.http.scaladsl.client.RequestBuilding._
import akka.http.scaladsl.model.Uri
import akka.http.scaladsl.model.Uri.Query
import akka.stream.Materializer
import id.kawalc1.ProbabilitiesResponse

import scala.concurrent.{ ExecutionContext, Future }

case class Transform(transformedUrl: Option[String], transformedUri: Option[String], similarity: Double, success: Boolean, hash: String)

case class Extracted(probabilities: Seq[Double], filename: String)

case class Numbers(id: String, shortName: String, displayName: String, extracted: Seq[Extracted])

case class Extraction(numbers: Seq[Numbers], digitArea: String)

case class Probabilities(id: String, probabilitiesForNumber: Seq[Seq[Double]])

case class ProbabilitiesRequest(configFile: String, probabilities: Seq[Probabilities])

class KawalC1Client(baseUrl: String)(implicit
  val system: ActorSystem,
  val mat: Materializer,
  val ec: ExecutionContext)
  extends HttpClientSupport
  with JsonSupport {

  def alignPhoto(
    kelurahan: Int,
    tps: Int,
    photoUrl: String,
    quality: Int,
    formConfig: String,
    featureAlgorithm: String): Future[Either[Response, Transform]] = {
    val url = Uri(s"$baseUrl/align/$kelurahan/$tps/$photoUrl=s$quality")
      .withQuery(
        Query(
          "storeFiles" -> "true",
          "baseUrl" -> "http://lh3.googleusercontent.com",
          "configFile" -> formConfig,
          "featureAlgorithm" -> featureAlgorithm))
    execute[Transform](Get(url))
  }

  def extractNumbers(kelurahan: Int, tps: Int, photoUrl: String, formConfig: String): Future[Either[Response, Extraction]] = {

    val url = Uri(s"$baseUrl/extract/$kelurahan/$tps/$photoUrl")
      .withQuery(Query("baseUrl" -> "https://storage.googleapis.com/kawalc1/static/transformed", "configFile" -> formConfig))
    execute[Extraction](Get(url))
  }

  def processProbabilities(
    kelurahan: Int,
    tps: Int,
    numbers: Seq[Numbers],
    formConfig: String): Future[Either[Response, ProbabilitiesResponse]] = {

    val probs = numbers.map { n =>
      Probabilities(n.id, n.extracted.map(_.probabilities))
    }
    val request = ProbabilitiesRequest(configFile = formConfig, probabilities = probs)
    execute[ProbabilitiesResponse](Post(Uri(s"$baseUrl/processprobs"), request))
  }

}
