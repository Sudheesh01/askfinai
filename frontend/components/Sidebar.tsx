import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface SidebarProps {
  watchlist: string[];
  onRemove: (ticker: string) => void;
}

export default function Sidebar({ watchlist, onRemove }: SidebarProps) {
  return (
    <Card className="h-full space-y-4">
      <div>
        <h2 className="text-sm font-semibold text-fin-text">Watchlist</h2>
        <p className="text-xs text-fin-muted">Saved tickers (local JSON).</p>
      </div>
      <div className="space-y-2">
        {watchlist.length === 0 && <p className="text-xs text-fin-muted">No tickers yet.</p>}
        {watchlist.map((ticker) => (
          <div key={ticker} className="flex items-center justify-between rounded-lg border border-fin-border px-3 py-2">
            <span className="text-sm">{ticker}</span>
            <Button variant="outline" size="sm" onClick={() => onRemove(ticker)}>
              Remove
            </Button>
          </div>
        ))}
      </div>
    </Card>
  );
}
