package id.kawalc1

import akka.actor.ActorSystem
import akka.stream.ActorMaterializer
import com.typesafe.scalalogging.LazyLogging
import id.kawalc1.cli.{ CrawlerConf, Tool }
import id.kawalc1.clients.{ KawalC1Client, KawalPemiluClient }
import id.kawalc1.database.ResultsTables
import id.kawalc1.services.{ BlockingSupport, PhotoProcessor }
import slick.jdbc
import slick.jdbc.SQLiteProfile
import slick.jdbc.SQLiteProfile.api._

import scala.concurrent.ExecutionContext
import scala.concurrent.duration._
import scala.language.reflectiveCalls

object Crawler extends App with LazyLogging with BlockingSupport {
  override def duration: FiniteDuration = 1.hour

  implicit val system: ActorSystem = ActorSystem("crawler")
  implicit val materializer: ActorMaterializer = ActorMaterializer()
  implicit val executionContext: ExecutionContext = system.dispatcher

  val conf = new CrawlerConf(args.toSeq)
  val myTool = new Tool(conf)

  private val remote = "https://kawalc1.appspot.com"
  private val local = "http://localhost:8000"

  val processor =
    new PhotoProcessor(new KawalC1Client(local), new KawalPemiluClient("https://kawal-c1.appspot.com/api/c"))
  val tpsDb = Database.forConfig("tpsDatabase")
  val kelurahanDatabase = Database.forConfig("kelurahanDatabase")
  val resultsDatabase = Database.forConfig("verificationResults")

  def process(
    phase: String,
    func: (SQLiteProfile.backend.Database, SQLiteProfile.backend.Database, Long, Long) => Long,
    sourceDb: SQLiteProfile.backend.Database,
    targetDb: SQLiteProfile.backend.Database,
    start: Long,
    batchSize: Long): Unit = {
    val amount = func(sourceDb, targetDb, start, batchSize)
    logger.info(s"Processed $amount in phase $phase")
  }

  def createDb(schema: jdbc.SQLiteProfile.SchemaDescription, database: SQLiteProfile.backend.Database, drop: Boolean = false): Unit = {
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
      val phase = c.Process.phase()
      val offset = c.Process.offset.toOption.getOrElse(0)
      val batchSize = c.Process.batch.toOption.getOrElse(50)
      logger.info(s"Starting $phase at offset $offset, with batch size $batchSize")
      phase match {
        case "fetch" =>
          process("fetch", processor.fetch, kelurahanDatabase, tpsDb, offset, batchSize)
        case "align" =>
          process("align", processor.align, tpsDb, resultsDatabase, offset, batchSize)
        case "extract" =>
          process("extract", processor.extract, resultsDatabase, resultsDatabase, offset, batchSize)
        case "presidential" =>
          process("presidential", processor.processProbabilities, resultsDatabase, resultsDatabase, offset, batchSize)
      }
    })
  myTool.run()
  system.terminate()
}
