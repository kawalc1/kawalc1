package id.kawalc1.clients

import akka.actor.ActorSystem
import akka.http.scaladsl.client.RequestBuilding._
import akka.http.scaladsl.model.headers.{Authorization, OAuth2BearerToken}
import akka.stream.Materializer
import id.kawalc1._

import scala.concurrent.{ExecutionContext, Future}

case class SubmitResponse(ok: Boolean)
case class TpsId(id: String)
case class GetResultPostBody(data: TpsId)
class KawalPemiluClient(baseUrl: String)(implicit
                                         val system: ActorSystem,
                                         val mat: Materializer,
                                         val ec: ExecutionContext)
    extends HttpClientSupport
    with JsonSupport {

  def getKelurahanOld(number: Long): Future[Either[Response, KelurahanOld]] = {
    implicit val authorization = None
    execute[KelurahanOld](Get(s"$baseUrl/$number"))
  }

  def getKelurahan(number: Long, authClient: OAuthClient): Future[Either[Response, KelurahanResponse]] = {
    for {
      token <- authClient.refreshToken()
      auth <- Future.successful(
        Authorization(OAuth2BearerToken(token.getOrElse(throw new IllegalStateException("no token")).response.access_token)))
      resp <- {
        implicit val authorization: Option[Authorization] = Some(auth)
        execute[MaybeKelurahanResponse](Post(s"$baseUrl", GetResultPostBody(TpsId(s"$number"))))
      }
      finalResp <- {
        resp match {
          case Left(value) => Future.successful(Left(value))
          case Right(maybe: MaybeKelurahanResponse) =>
            maybe.result match {
              case Some(v) => Future.successful(Right(KelurahanResponse(v)))
              case None =>
                logger.warn("Retrying after 5 seconds")
                Thread.sleep(5000)
                implicit val authorization: Option[Authorization] = Some(auth)
                execute[MaybeKelurahanResponse](Post(s"$baseUrl", GetResultPostBody(TpsId(s"$number")))).map {
                  case Left(value)  => Left(value)
                  case Right(value) => Right(KelurahanResponse(value.result.get))
                }
            }
        }

      }
    } yield finalResp
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
