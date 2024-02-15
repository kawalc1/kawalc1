package id.kawalc1.clients

import akka.actor.ActorSystem
import akka.http.caching.LfuCache
import akka.http.caching.scaladsl.{ Cache, CachingSettings, LfuCacheSettings }
import akka.http.scaladsl.client.RequestBuilding._
import akka.http.scaladsl.model.headers.{ Authorization, OAuth2BearerToken }
import akka.stream.Materializer
import id.kawalc1._

import scala.concurrent.duration.DurationInt
import scala.concurrent.{ ExecutionContext, Future }

case class SubmitResponse(ok: Boolean)
case class TpsId(id: String, uid: String)
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

  private val defaultCachingSettings = CachingSettings(system)

  private val lfuCacheSettings: LfuCacheSettings =
    defaultCachingSettings.lfuCacheSettings
      .withInitialCapacity(1)
      .withMaxCapacity(1)
      .withTimeToLive(5.seconds)

  private val cache: Cache[String, Boolean] = LfuCache(defaultCachingSettings.withLfuCacheSettings(lfuCacheSettings))

  private def avoidThunderingHerds(seconds: Int): Future[Boolean] = {
    logger.info("Entering mutex...")
    cache.getOrLoad("mutex", _ => {
      Future {
        logger.info(s"Waiting ${seconds} seconds for rate limit to subside...")
        Thread.sleep(seconds * 1000L)
        true
      }
    })
  }

  def getKelurahan(number: Long, authClient: OAuthClient): Future[Either[Response, KelurahanResponse]] = {
    for {
      auth <- authClient.refreshToken().map(token => Authorization(OAuth2BearerToken(token.response.access_token)))
      resp <- getData(number, auth)
      finalResp <- resp match {
        case Left(value) => Future.successful(Left(value))
        case Right(value) if value.result.isDefined => Future.successful(Right(KelurahanResponse(value.result.get)))
        case Right(value) =>
          for {
            thunderingHerds <- {
              logger.info(s"Empty result for $number")
              val secondsToWait = if (value.error) { 10 } else { 1 }
              avoidThunderingHerds(secondsToWait)
            }
            auth <- authClient
              .refreshToken(force = thunderingHerds)
              .map(token => Authorization(OAuth2BearerToken(token.response.access_token)))
            data <- getData(number, auth)
          } yield {
            data match {
              case Left(value) => Left(value)
              case Right(value) if value.result.isDefined => Right(KelurahanResponse(value.result.get))
              case Right(_) =>
                logger.info(s"Still empty for $number")
                Left(Response(503, "Need to try later"))
            }
          }
      }
    } yield finalResp
  }

  private def getData(number: Long, auth: Authorization): Future[Either[Response, MaybeKelurahanResponse]] = {
    implicit val authorization: Option[Authorization] = None
    execute[MaybeKelurahanResponse](Post(s"$baseUrl", GetResultPostBody(TpsId(s"$number", Config.Application.userUid)))).map {
      case Left(value) if Seq(404, 500, 503).contains(value.code) =>
        logger.info(s"Got ${value.code} for tpsId: $number ${value.response}")
        Right(MaybeKelurahanResponse(None, error = true))
      case Left(value) => Left(value)
      case Right(value) => Right(value)
    }
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
