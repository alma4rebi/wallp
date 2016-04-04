from os.path import dirname, join as joinpath, basename
from shutil import copyfile
from datetime import datetime

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext

from ... import const


class ManageDBError(Exception):
	pass


class DB:

	def __init__(self):
		pass


	def create(self):
		pass


	def insert_data(self):
		# table list
		tables = [Source]

		# check if it has data file
		for table in tables:
			data_file_path = dirpath + table.__tablename__ + '.csv'
			if exists(data_file_path):
				csv = load(data_file_path)

				csv_cols = row[0]
				for row in csv:
					dict = {csv_col : row[i] } # optionally, eval 
					record = table(**dict)

					if not exists row:	# or pass the constraint exception
						session.add(record)

			session.commit()

		# handle exceptions

		# if yes, load it as csv
		# if a column type != String, eval it
		# insert data


	def upgrade(self, script_location, db_path, dest_rev):
		sa_url = 'sqlite:///' + db_path

		config = Config()
		config.set_main_option('script_location', script_location)
		config.set_main_option('sqlalchemy.url', sa_url)

		config.config_file_name = joinpath(dirname(script_location), 'alembic.ini')

		script = ScriptDirectory.from_config(config)

		def upgrade(rev, context):
			return script._upgrade_revs(dest_rev, rev)

		with EnvironmentContext(
			config,
			script,
			fn		= upgrade,
			as_sql		= False,
			starting_rev	= None,
			destination_rev	= dest_rev,
			tag		= None
		):
			script.run_env()


	def backup(self, dest_path=None):
		if dest_path is None:
			dest_path = dirname(const.db_path)

		db_path = const.db_path

		dt = datetime.now().strftime('%d_%b_%Y_%H_%M_%S').lower()
		dest_db_path = joinpath(dest_path, dt + '_' + basename(db_path))

		try:
			copyfile(db_path, dest_db_path)
		except (IOError, OSError) as e:
			raise ManageDBError(str(e))

		return dest_db_path


	def restore(self, src_path=None):
		pass


