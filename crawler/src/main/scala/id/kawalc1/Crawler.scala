package id.kawalc1

import akka.actor.ActorSystem
import akka.stream.ActorMaterializer
import akka.stream.scaladsl.Source
import com.typesafe.scalalogging.LazyLogging
import id.kawalc1.Config.Application
import id.kawalc1.cli.{ CrawlerConf, Tool }
import id.kawalc1.clients._
import id.kawalc1.database.CustomPostgresProfile.api._
import id.kawalc1.database.{ CustomPostgresProfile, DetectionResult, ResultsTables, TpsTables }
import id.kawalc1.services.{ BlockingSupport, PhotoProcessor }
import org.json4s.native.Serialization

import java.io.{ File, PrintWriter }
import java.net.URL
import java.time.LocalDateTime
import scala.concurrent.ExecutionContext
import scala.concurrent.duration._
import scala.language.reflectiveCalls

case class BatchParams(start: Long, batchSize: Long, threads: Int, limit: Option[Int], offset: Int = 0)

object Crawler extends App with LazyLogging with BlockingSupport with JsonSupport {
  override def duration: FiniteDuration = 1.hour

  implicit val system: ActorSystem = ActorSystem("crawler")
  implicit val materializer: ActorMaterializer = ActorMaterializer()
  implicit val executionContext: ExecutionContext = system.dispatcher

  val conf = new CrawlerConf(args.toSeq)
  val myTool = new Tool(conf)

  private val kawalPemiluClient = new KawalPemiluClient("https://kp24-fd486.et.r.appspot.com/h")
  val processor = new PhotoProcessor(kawalPemiluClient)
  val tpsDb = Database.forConfig("tpsDatabase")
  private val kelurahanDatabase = Database.forConfig("verificationResults")
  val resultsDatabase = Database.forConfig("verificationResults")

  def process(
    phase: String,
    func: (CustomPostgresProfile.backend.Database, CustomPostgresProfile.backend.Database, KawalC1Client, BatchParams) => Long,
    sourceDb: CustomPostgresProfile.backend.Database,
    targetDb: CustomPostgresProfile.backend.Database,
    client: KawalC1Client,
    params: BatchParams): Unit = {
    val amount = func(sourceDb, targetDb, client, params)
    logger.info(s"Processed $amount in phase $phase")
  }

  def createDb(
    schema: CustomPostgresProfile.SchemaDescription,
    database: CustomPostgresProfile.backend.Database,
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
    conf.Submit,
    (c: CrawlerConf) => {
      val token = c.Submit.token.toOption.get
      val force = c.Submit.force.toOption.getOrElse(false)
      val name = c.Submit.name.toOption.get
      name match {
        case "submit" =>
          val unverifieds = resultsDatabase.run(TpsTables.tpsUnverifiedQuery.drop(14992).result).futureValue.toList
          val futures = Source(unverifieds).mapAsync(6) {
            t: SingleOldTps =>
              val body = t.verification.c1.get.halaman match {
                case Some("1") =>
                  val p = t.verification.sum.get.asInstanceOf[SingleSum]
                  Approval(t.kelurahanId, "", t.tpsId, SingleSum(p.jum), t.imageId.get, C1(Some(Plano.NO), FormType.PPWP, Some("1")))
                case Some("2") =>
                  val p = t.verification.sum.get.asInstanceOf[PresidentialLembar2]
                  Approval(
                    t.kelurahanId,
                    "",
                    t.tpsId,
                    PresidentialLembar2(p.pas1, p.pas2, p.sah, p.tSah),
                    t.imageId.get,
                    C1(Some(Plano.NO), FormType.PPWP, Some("2")))
              }
              kawalPemiluClient.submitApprove("https://upload.kawalpemilu.org", token, body).map {
                case Right(resp) =>
                  Some(true)
                case Left(err) =>
                  println(s"failed $err")
                  None
              }
          }
          futures.runFold(Seq.empty[Option[Boolean]])(_ :+ _).futureValue

        case "switch" =>
          val client = new FireStoreClient("https://firestore.googleapis.com/v1/projects/kawal-c1/databases/(default)/documents/t2/")
          val terbaliks = resultsDatabase.run(ResultsTables.terbaliksQuery.drop(1).result).futureValue
          var i = 0
          terbaliks.foreach {
            t =>
              i = i + 1
              val submit =
                for {
                  halaman1 <- client.getDocId(t.kelurahan, t.tps, t.hal2Photo, token)
                  halaman2 <- client.getDocId(t.kelurahan, t.tps, t.hal1Photo, token)
                  moved1 <- {
                    val body = Approval(
                      t.kelurahan,
                      "",
                      t.tps,
                      PresidentialLembar2(t.pas1, t.pas2, t.jumlah, t.tidakSah),
                      halaman1.imageId,
                      C1(Some(Plano.NO), FormType.PPWP, Some("2")))
                    kawalPemiluClient.submitApprove("https://upload.kawalpemilu.org", token, body)
                  }
                  moved2 <- {
                    val body =
                      Approval(t.kelurahan, "", t.tps, SingleSum(t.php), halaman2.imageId, C1(Some(Plano.NO), FormType.PPWP, Some("1")))
                    kawalPemiluClient.submitApprove("https://upload.kawalpemilu.org", token, body)
                  }
                } yield { moved2 }
              submit.futureValue
              println(s"processed $i")
            //            Thread.sleep(200)

          }

        case "problems" =>
          val problems: Seq[Problem] = resultsDatabase.run(ResultsTables.problemsToReportQuery.result).futureValue

          problems.foreach {
            x =>
              println(s"problem $x")

              val success = kawalPemiluClient.subitProblem("https://upload.kawalpemilu.org", token, x).futureValue
              Thread.sleep(400)
              success match {
                case Right(submitted) =>
                  val reported = ProblemReported(x.kelId, "", x.tpsNo, x.url, x.reason)
                  resultsDatabase.run(ResultsTables.problemsReportedQuery.insertOrUpdate(reported)).futureValue
                case Left(err) =>
                  println(s"Error: $err")
                  resultsDatabase.run(ResultsTables.problemsQuery.insertOrUpdate(x.copy(response_code = Some(err.code)))).futureValue
              }
            //        println(s"$success")
          }
      }
    })

  myTool.registerSubcmdHandler(
    conf.Stats,
    (c: CrawlerConf) => {
      val on = c.Stats.on()
      on match {
        case "det-duplicated" =>
          val aligned = resultsDatabase.run(ResultsTables.detectionsQuery.result).futureValue
          val grouped: Map[String, Seq[DetectionResult]] = aligned.groupBy((x: DetectionResult) => s"${x.hash.getOrElse("")}")
          println(s"Groups size: ${grouped.size}")
          val pw = new PrintWriter(new File("scan-dups.csv"))
          val duplicates = grouped.filter {
            case (hash, group: Seq[DetectionResult]) =>
              val details = group.map(x => s"${x.kelurahan},${x.tps}").toSet

              if (details.size > 1 && hash != "" && hash != "hash") {
                val jumlahSet = group.map(x => s"${x.jumlah}").toSet
                if (jumlahSet.size == 1) {
                  grouped(hash).foreach { x: DetectionResult =>
                    pw.println(s"${x.photo},${x.kelurahan},${x.tps},${details.size},$hash")
                  }
                }

              }
              group.size > 1
          }
          pw.close()
          //              if (group.size > 1) println(s"${details.head},${group.size},https://upload.kawalpemilu.org/t/${group.head.id}")
          //              group.size > 1 //&& group.map(x => s"${x.id},${x.tps}").toSet.size > 1

          println(s"Size ${duplicates.size}")
      }
    })
  myTool.registerSubcmdHandler(
    conf.CreateDb,
    (c: CrawlerConf) => {
      val phase = c.CreateDb.name
      val drop = c.CreateDb.drop()
      phase() match {
        case "terbalik" =>
          createDb(ResultsTables.terbaliksQuery.schema, resultsDatabase, drop)
        case "problems" =>
          createDb(ResultsTables.problemsQuery.schema, resultsDatabase, drop)
        case "problems-reported" =>
          createDb(ResultsTables.problemsReportedQuery.schema, resultsDatabase, drop)
        case "forms-processed" =>
          createDb(ResultsTables.formsProcessedQuery.schema, resultsDatabase, drop)
        case "detect" =>
          createDb(ResultsTables.detectionsQuery.schema, resultsDatabase, drop)
        case "fetch" =>
          val sedotDatabase = Database.forConfig("sedotDatabase")
          createDb(TpsTables.tpsQuery.schema, sedotDatabase, drop)
          createDb(TpsTables.tpsPhotoQuery.schema, resultsDatabase, drop)
          createDb(TpsTables.tpsQuery.schema, resultsDatabase, drop)
        case "align" =>
          createDb(ResultsTables.alignResultsQuery.schema, resultsDatabase, drop)
        case "extract" =>
          createDb(ResultsTables.extractResultsQuery.schema, resultsDatabase, drop)
        case "presidential" =>
          createDb(ResultsTables.presidentialResultsQuery.schema, resultsDatabase, drop)
        case "tps-unprocessed" =>
          createDb(TpsTables.tpsUnverifiedQuery.schema, resultsDatabase, drop)

      }
    })

  val urlie = "http://lh3.googleusercontent.com/6TSO9UKWsCHekURjdjoWOEKwYbUjUUsWUJqYVB_3VWVmm9TLvfoaXbPXLmgE8p0PbQtsEQ1OFaDC0FRSMbw"
  myTool.registerSubcmdHandler(
    conf.Process,
    (c: CrawlerConf) => {
      val phase = c.Process.phase()
      val offset = c.Process.offset.toOption.getOrElse(0)
      val batchSize = c.Process.batch.toOption.getOrElse(50)
      val threads = c.Process.threads.toOption.getOrElse(10)
      val limit = c.Process.limit.toOption
      val maybeToken = c.Process.refreshToken.toOption
      val service = c.Process.service.toOption.getOrElse(Application.kawalC1UrlLocal)
      val continuous = c.Process.continuous.getOrElse(false)
      val batchParams = BatchParams(offset, batchSize, threads, limit, offset)
      val kawalC1Client = new KawalC1Client(service)
      val url = new URL(service)
      logger.info(s"Starting $phase with ${Serialization.write(batchParams)}")
      phase match {
        case "test" =>
          val howMany = resultsDatabase.run(ResultsTables.tpsToDetectQuery(offset).result).futureValue.length
          println(s"This much: $howMany")
        case "download-original" =>
          process("download-original", processor.downloadOriginal, kelurahanDatabase, resultsDatabase, kawalC1Client, batchParams)
        case "fetch" =>
          var continue = true
          var round = 0
          do {
            implicit val refreshToken: String = maybeToken.getOrElse(throw new IllegalArgumentException("Refresh token for KP required"))
            implicit val authClient = new OAuthClient("https://securetoken.googleapis.com/v1", refreshToken)
            authClient.refreshToken().futureValue
            process("fetch", processor.fetch, kelurahanDatabase, resultsDatabase, kawalC1Client, batchParams)
            continue = continuous
            if (continuous) {
              round += 1
              logger.info(s"Giving it a while... for round $round")
              Thread.sleep(20000)
            }
          } while (continue)
        case "align" =>
          val howMany = resultsDatabase.run(ResultsTables.tpsToAlignQuery(Plano.NO).result).futureValue.length
          logger.info(s"Will align $howMany forms")
          process("align", processor.align, resultsDatabase, resultsDatabase, kawalC1Client, batchParams)
        case "extract" =>
          val howMany = resultsDatabase.run(ResultsTables.tpsToExtractQuery.result).futureValue.length
          logger.info(s"Will extract $howMany forms with $batchParams")
          process("extract", processor.extract, resultsDatabase, resultsDatabase, kawalC1Client, batchParams)
        case "presidential" =>
          process("presidential", processor.processProbabilities, resultsDatabase, resultsDatabase, kawalC1Client, batchParams)
        case "detect" =>
          var continue = true
          do {
            val outputFile = new File(s"batches/detections-${LocalDateTime.now()}-${url.getHost}.csv")
            val howMany = resultsDatabase.run(ResultsTables.tpsToDetectQuery(offset).result).futureValue.length
            println(s"Will detect: $howMany")
            process("detections", processor.processDetections, resultsDatabase, resultsDatabase, kawalC1Client, batchParams)
            continue = continuous
            if (continuous) {
              logger.info("Giving it a while...")
              Thread.sleep(20000)
            }
          } while (continue)
        //        case "tps-unprocessed" =>
        //          implicit val pw = new PrintWriter(new File(s"batches/felix-${LocalDateTime.now()}-${url.getHost}.csv"))
        //          val howMany = resultsDatabase.run(TpsTables.tpsUnverifiedQuery.result).futureValue.length
        //          println(s"Will detect: $howMany")
        //          process("detections", processor.processUnverifiedDetections, resultsDatabase, resultsDatabase, kawalC1Client, batchParams)
        //        case "roi" =>
        //          implicit val pw = new PrintWriter(new File(s"batches/rois-${LocalDateTime.now()}-${url.getHost}.csv"))
        //          val howMany = resultsDatabase.run(ResultsTables.tpsToRoiQuery.result).futureValue.length
        //          println(s"Will detect: $howMany")
        //          process("rois", processor.processRois, resultsDatabase, resultsDatabase, kawalC1Client, batchParams)
      }
    })
  myTool.run()
  system.terminate()
}
