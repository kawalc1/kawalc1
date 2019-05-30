package id.kawalc1.clients

import akka.actor.ActorSystem
import akka.http.scaladsl.client.RequestBuilding._
import akka.http.scaladsl.model.headers.{ Authorization, OAuth2BearerToken }
import akka.stream.Materializer
import id.kawalc1.{ Approval, Kelurahan, Problem }

import scala.concurrent.{ ExecutionContext, Future }

case class SubmitResponse(ok: Boolean)
class KawalPemiluClient(baseUrl: String)(implicit val system: ActorSystem, val mat: Materializer, val ec: ExecutionContext)
  extends HttpClientSupport
  with JsonSupport {

  def getKelurahan(number: Long): Future[Either[Response, Kelurahan]] = {
    implicit val authorization = None
    execute[Kelurahan](Get(s"$baseUrl/$number"))
  }

  def subitProblem(baseUrl: String, token: String, problem: Problem): Future[Either[Response, SubmitResponse]] = {
    implicit val authorization = Some(Authorization(OAuth2BearerToken(token)))

    val request = Post(s"$baseUrl/api/problem", problem)
    execute[SubmitResponse](request)
  }

  def submitApprove(baseUrl: String, token: String, problem: Approval): Future[Either[Response, SubmitResponse]] = {
    implicit val authorization = Some(Authorization(OAuth2BearerToken(token)))

    val request = Post(s"$baseUrl/api/approve", problem)
    execute[SubmitResponse](request)
  }
}
