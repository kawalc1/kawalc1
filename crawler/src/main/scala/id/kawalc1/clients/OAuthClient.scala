package id.kawalc1.clients

import akka.actor.ActorSystem
import akka.http.scaladsl.client.RequestBuilding._
import akka.stream.Materializer
import id.kawalc1.Config.Application

import java.time.Instant
import java.time.temporal.ChronoUnit
import scala.concurrent.{ExecutionContext, Future}

case class RefreshTokenResponse(access_token: String,
                                expires_in: String,
                                token_type: String,
                                refresh_token: String,
                                id_token: String,
                                user_id: String,
                                project_id: String)
case class ResponseWithTime(issuedAt: Instant, response: RefreshTokenResponse)
case class RefreshTokenRequest(grant_type: String = "refresh_token", refresh_token: String)

class OAuthClient(baseUrl: String, initialToken: String)(implicit val system: ActorSystem, val mat: Materializer, val ec: ExecutionContext)
    extends HttpClientSupport
    with JsonSupport {

  private var currentToken: Option[ResponseWithTime] = None

  def refreshToken(force: Boolean = false): Future[Either[Response, ResponseWithTime]] = {
    val expired                = currentToken.forall(x => Instant.now.minus(50, ChronoUnit.MINUTES).isAfter(x.issuedAt))
    implicit val authorization = None
    if (expired || force) {
      for {
        response <- execute[RefreshTokenResponse](
          Post(s"$baseUrl/token?key=${Application.kpApiKey}",
               RefreshTokenRequest(refresh_token = currentToken.map(_.response.refresh_token).getOrElse(initialToken))))
          .map(_.map(ResponseWithTime(Instant.now(), _)))
      } yield {
        response.foreach { x: ResponseWithTime =>
          logger.warn(s"Updated token to ${x.issuedAt}, ${x.response.refresh_token}")
          currentToken = Some(x)
        }
        response
      }

    } else {
      Future.successful(Right(currentToken.get))
    }
  }

}
