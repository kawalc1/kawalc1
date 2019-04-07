package id.kawalc1

import akka.actor.ActorSystem
import akka.http.scaladsl.model.Uri
import akka.stream.ActorMaterializer
import com.typesafe.scalalogging.LazyLogging
import id.kawalc1.clients.{KawalC1Client, KawalPemiluClient, Transform}
import id.kawalc1.database.{AlignResult, ExtractResult, ResultsTables, TpsTables}
import id.kawalc1.services.{AlignedPicture, PhotoProcessor, TpsFetcher}
import slick.jdbc.SQLiteProfile
import slick.jdbc.SQLiteProfile.api._

import scala.concurrent.duration._
import scala.concurrent.{Await, ExecutionContext}

object Crawler extends App with LazyLogging {

  implicit val system: ActorSystem                = ActorSystem("crawler")
  implicit val materializer: ActorMaterializer    = ActorMaterializer()
  implicit val executionContext: ExecutionContext = system.dispatcher

  if (args.isEmpty) {
    println("Usage")
    println("Crawler fullSync|align|(createDb results|extract)")
    System.exit(0)
  }
  val arg = args(0)

  val tpsDb: SQLiteProfile.backend.Database = Database.forConfig("tpsDatabase")
  val kelurahanDatabase                     = Database.forConfig("kelurahanMinimalDatabase")
  val resultsDatabase                       = Database.forConfig("verificationResults")

  def createDatabase() = {
    val create = DBIO.seq(TpsTables.tpsQuery.schema.drop, TpsTables.tpsQuery.schema.create)
    tpsDb.run(create)
  }

  val processor = new PhotoProcessor(new KawalC1Client("http://localhost:8000"))

  arg match {
    case "fullSync" =>
      Await.result(createDatabase(), 1.minute)
      Await.result(new TpsFetcher(new KawalPemiluClient("https://kawal-c1.appspot.com/api/c"),
                                  kelurahanDatabase,
                                  tpsDb).ingestAllTps(),
                   1.hour)
    case "align" =>
      val url =
        "http://lh3.googleusercontent.com/112k-9-NflCZLN-V40c-viTCUamyzGzNPCmwtnlFaSCUAYfGdhESqqj0OhDuxwop8NMmLd1Q35ClHCPTqLt-"
      val results = for {
        tps <- tpsDb.run(
          TpsTables.tpsQuery
            .filter(_.photo === url)
            .filter(_.formType === FormType.PPWP.value)
            .result)
        results <- processor.alignPhoto(tps)
        inserted <- {
          val toInsert = results.flatMap {
            case Right(pic: AlignResult) => Some(pic)
            case Left(err) =>
              logger.warn(s"failed to align $err")
              None
          }
          resultsDatabase.run(DBIO.sequence(ResultsTables.upsertAlign(toInsert)))
        }
      } yield inserted
      val res = Await.result(results, 1.hour)
      logger.info(s"Aligned ${res.size} photo(s)")

    case "extract" =>
      val extraction = for {
        alignResults   <- resultsDatabase.run(ResultsTables.resultsQuery.result)
        extractResults <- processor.extractNumbers(alignResults)
        inserted <- {
          val toInsert = extractResults.flatMap {
            case Right(e: ExtractResult) => Some(e)
            case Left(err) =>
              logger.warn(s"failed to extract $err")
              None
          }
          resultsDatabase.run(DBIO.sequence(ResultsTables.upsertExtract(toInsert)))
        }
      } yield inserted
      val res = Await.result(extraction, 1.hour)
      logger.info(s"Extracted ${res.size} photo(s)")

    case "createDb" =>
      args(1) match {
        case "results" =>
          val resultsCreate = DBIO.seq(ResultsTables.resultsQuery.schema.create)
          Await.result(resultsDatabase.run(resultsCreate), 1.minute)
          logger.info("created results Database")
        case "extract" =>
          val extractCreate = DBIO.seq(ResultsTables.extractResultsQuery.schema.create)
          Await.result(resultsDatabase.run(extractCreate), 1.minute)
          logger.info("created extraction Database")
      }
  }
  system.terminate()

}
