package id.kawalc1

import com.typesafe.scalalogging.LazyLogging
import id.kawalc1.clients.JsonSupport
import id.kawalc1.database.TpsTables
import org.json4s.native.Serialization
import org.scalatest.{Matchers, WordSpec}
import slick.jdbc.H2Profile.api._

import scala.io.Source
import scala.language.reflectiveCalls

class DatabaseSpecs extends WordSpec with Matchers with FutureMatcher with LazyLogging with JsonSupport {
  "Database" should {
    "Store TPS results" in {
      val db                       = Database.forConfig("tpsTestDatabase")
      val response                 = Source.fromURL(getClass.getResource("/hierarchy/5171021003.json")).mkString
      val kelurahan                = Serialization.read[KelurahanResponse](response)
      val tpses: Seq[SingleTpsDao] = Kelurahan.toTps(kelurahan)
      val tpsJson                  = Serialization.writePretty(tpses)
      println(s"$tpsJson")
      val setup =
        DBIO.seq(TpsTables.tpsQuery.schema.dropIfExists, TpsTables.tpsQuery.schema.create, TpsTables.tpsQuery ++= tpses)
      try {
        db.run(setup).futureValue
        db.run(TpsTables.tpsQuery.result).futureValue
      } finally db.close()
    }
  }
}
