package id.kawalc1.clients

import akka.actor.ActorSystem
import akka.http.caching.LfuCache
import akka.http.caching.scaladsl.{ Cache, CachingSettings, LfuCacheSettings }
import akka.http.scaladsl.client.RequestBuilding._
import akka.stream.Materializer
import id.kawalc1.Config.Application

import java.time.Instant
import scala.concurrent.duration.DurationInt
import scala.concurrent.{ ExecutionContext, Future }

case class RefreshTokenResponse(
  access_token: String,
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

  private val defaultCachingSettings = CachingSettings(system)

  private var initToken: Option[String] = None

  private val lfuCacheSettings: LfuCacheSettings =
    defaultCachingSettings.lfuCacheSettings
      .withInitialCapacity(1)
      .withMaxCapacity(1)
      .withTimeToLive(5.minutes)

  private val cache: Cache[String, ResponseWithTime] = LfuCache(defaultCachingSettings.withLfuCacheSettings(lfuCacheSettings))

  private def getCachedTicket(token: String): Future[ResponseWithTime] = {
    cache.getOrLoad(
      "token",
      _ => {
        implicit val authorization = None
        val response =
          execute[RefreshTokenResponse](Post(s"$baseUrl/token?key=${Application.kpApiKey}", RefreshTokenRequest(refresh_token = token)))
            .map(_.map(ResponseWithTime(Instant.now(), _)))
        response.map {
          case Left(value) => throw new IllegalStateException(s"Could not refresh token: ${value.code} ${value.response}")
          case Right(value) => {
            logger.info(s"Refreshed token ${value.issuedAt} ${value.response.refresh_token}")
            value
          }
        }
      })
  }

  def refreshToken(force: Boolean = false): Future[ResponseWithTime] = {
    (initToken match {
      case Some(value) =>
        getCachedTicket(value)
      case None =>
        getCachedTicket(initialToken)
    }).map { x =>
      this.initToken = Some(x.response.refresh_token)
      x
    }
  }

}
