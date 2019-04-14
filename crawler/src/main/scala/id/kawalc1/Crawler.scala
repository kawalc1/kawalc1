package id.kawalc1

import akka.actor.ActorSystem
import akka.stream.ActorMaterializer
import com.typesafe.scalalogging.LazyLogging
import id.kawalc1.cli.{ CrawlerConf, Tool }
import id.kawalc1.clients.{ KawalC1Client, KawalPemiluClient }
import id.kawalc1.database.ResultsTables
import id.kawalc1.services.{ BlockingSupport, PhotoProcessor, TpsFetcher }
import slick.jdbc
import slick.jdbc.SQLiteProfile
import slick.jdbc.SQLiteProfile.api._

import scala.concurrent.{ ExecutionContext, Future }
import scala.concurrent.duration._
import scala.language.reflectiveCalls

object Crawler extends App with LazyLogging with BlockingSupport {
  override def duration: FiniteDuration = 1.hour

  implicit val system: ActorSystem = ActorSystem("crawler")
  implicit val materializer: ActorMaterializer = ActorMaterializer()
  implicit val executionContext: ExecutionContext = system.dispatcher

  val conf = new CrawlerConf(args.toSeq)
  val myTool = new Tool(conf)

  val processor = new PhotoProcessor(new KawalC1Client("http://localhost:8000"))
  val tpsDb = Database.forConfig("tpsDatabase")
  val kelurahanDatabase = Database.forConfig("kelurahanDatabase")
  val resultsDatabase = Database.forConfig("verificationResults")

  def process(
    phase: String,
    func: (SQLiteProfile.backend.Database, SQLiteProfile.backend.Database) => Future[Seq[Int]],
    sourceDb: SQLiteProfile.backend.Database,
    targetDb: SQLiteProfile.backend.Database): Unit = {
    func(sourceDb, targetDb).map { res =>
      logger.info(s"Aligned ${res.size} photo(s)")
    }.futureValue
  }

  def createDb(
    schema: jdbc.SQLiteProfile.SchemaDescription,
    database: SQLiteProfile.backend.Database,
    drop: Boolean = false): Unit = {
    val action = if (drop) {
      DBIO.seq(schema.drop, schema.create)
    } else {
      DBIO.seq(schema.create)
    }
    database
      .run(action)
      .map { _ =>
        logger.info(s"created Database \n ${schema.createStatements.toSeq.mkString("\n")}")
      }
      .futureValue
  }

  myTool.registerSubcmdHandler(
    conf.CreateDb,
    (c: CrawlerConf) => {
      val phase = c.CreateDb.name
      val drop = c.CreateDb.drop()
      phase() match {
        case "align" =>
          createDb(ResultsTables.alignResultsQuery.schema, resultsDatabase, drop)
        case "extract" =>
          createDb(ResultsTables.extractResultsQuery.schema, resultsDatabase, drop)
        case "presidential" =>
          createDb(ResultsTables.presidentialResultsQuery.schema, resultsDatabase, drop)
      }
    })

  myTool.registerSubcmdHandler(
    conf.Process,
    (c: CrawlerConf) => {
      val phase = c.Process.phase
      phase() match {
        case "fetch" =>
          new TpsFetcher(
            new KawalPemiluClient("https://kawal-c1.appspot.com/api/c"),
            kelurahanDatabase,
            tpsDb).ingestAllTps().futureValue
        case "align" =>
          process("align", processor.align, tpsDb, resultsDatabase)
        case "extract" =>
          process("extract", processor.extract, resultsDatabase, resultsDatabase)
        case "presidential" =>
          process("presidential", processor.processProbabilities, resultsDatabase, resultsDatabase)
      }
    })
  myTool.run()
  system.terminate()
}
