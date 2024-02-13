package id.kawalc1.database

import com.github.tminglei.slickpg._

trait CustomPostgresProfile extends ExPostgresProfile {
  def pgjson = "jsonb"

  override protected def computeCapabilities: Set[slick.basic.Capability] =
    super.computeCapabilities + slick.jdbc.JdbcCapabilities.insertOrUpdate

  override val api = PostgresJsonSupportAPI

  object PostgresJsonSupportAPI extends API {}
}

object CustomPostgresProfile extends CustomPostgresProfile
