import logging
import sys
import click
from dotenv import load_dotenv
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


@click.command()
@click.option(
    "--export-csv",
    type=click.Path(),
    help="Export giveaways to CSV file",
    default=None,
)
@click.option(
    "--force-refresh",
    is_flag=True,
    help="Force refresh cache (ignore TTL)",
)
@click.option(
    "--init-db",
    is_flag=True,
    help="Initialize database tables",
)
@click.option(
    "--scraper-mode",
    type=click.Choice(["auto", "requests", "browser"], case_sensitive=False),
    default=None,
    help="Fetch mode: auto (default), requests, or browser",
)
@click.option(
    "--headed",
    is_flag=True,
    help="Show a visible browser window in Playwright browser mode",
)
def main(
    export_csv: Optional[str],
    force_refresh: bool,
    init_db: bool,
    scraper_mode: Optional[str],
    headed: bool,
):
    """
    Gleam.io Giveaway Scraper - Browse and open giveaways interactively

    Examples:
        gleam-scraper              # Run interactive mode
        gleam-scraper --force-refresh  # Refresh cache and run interactive mode
        gleam-scraper --export-csv giveaways.csv  # Export to CSV
        gleam-scraper --init-db    # Initialize database
        gleam-scraper --scraper-mode browser --force-refresh  # Browser runtime
        gleam-scraper --scraper-mode browser --headed --force-refresh  # Visible browser
    """
    try:
        from src.cache import CacheManager
        from src.csv_export import CSVExporter
        from src.database import SessionLocal, init_db as init_database
        from src.ui import SimpleTUI

        # Initialize database if requested
        if init_db:
            click.echo("Initializing database...")
            init_database()
            click.echo("✓ Database initialized successfully")
            return

        # Create database session
        db = SessionLocal()
        cache_manager = CacheManager(db)

        # Get giveaways
        click.echo("Loading giveaways...")
        try:
            giveaways = cache_manager.get_giveaways(
                force_refresh=force_refresh,
                scraper_mode=scraper_mode.lower() if scraper_mode else None,
                playwright_headless=False if headed else None,
            )
        except Exception as e:
            click.echo(f"✗ Error loading giveaways: {e}", err=True)
            logger.error(f"Error: {e}", exc_info=True)
            sys.exit(1)

        if not giveaways:
            click.echo("✗ No giveaways found", err=True)
            sys.exit(1)

        click.echo(f"✓ Loaded {len(giveaways)} giveaways\n")

        # Export to CSV if requested
        if export_csv:
            success = CSVExporter.export(giveaways, export_csv)
            if success:
                click.echo(f"✓ Exported to {export_csv}")
            else:
                click.echo(f"✗ Failed to export to {export_csv}", err=True)
                sys.exit(1)
            return

        # Run interactive mode
        tui = SimpleTUI(giveaways)
        tui.run()

    except KeyboardInterrupt:
        click.echo("\n✓ Exiting...")
    except Exception as e:
        click.echo(f"✗ Fatal error: {e}", err=True)
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()


if __name__ == "__main__":
    main()
