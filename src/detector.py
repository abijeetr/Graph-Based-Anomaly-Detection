import sqlite3
import pandas as pd
import networkx as nx
from sklearn.ensemble import IsolationForest

DB_FILE = "financial_data.db"

def fetch_data_from_db(db_file):
    print("Connecting to database to fetch transactions...")
    try:
        conn = sqlite3.connect(db_file, timeout=10)
        df = pd.read_sql_query("SELECT sender_id, receiver_id, amount FROM transactions", conn)
        conn.close()
        print(f"Successfully fetched {len(df)} transactions.")
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def detect_anomalies(df):
    if df is None: return None, None

    print("Building graph from transaction data...")
    G = nx.from_pandas_edgelist(df, 'sender_id', 'receiver_id', ['amount'], create_using=nx.DiGraph())

    print("Engineering graph features for each user...")
    features_list = []
    node_list = sorted(list(G.nodes()))

    total_out_amount = G.out_degree(weight='amount')
    total_in_amount = G.in_degree(weight='amount')

    for node in node_list:
        features = {
            'user_id': node,
            'out_degree': G.out_degree(node),
            'in_degree': G.in_degree(node),
            'total_amount_sent': total_out_amount[node],
            'total_amount_received': total_in_amount[node]
        }
        features_list.append(features)
        
    features_df = pd.DataFrame(features_list).set_index('user_id')

    print("Initializing and running IsolationForest model...")
    model = IsolationForest(contamination=0.01, random_state=42, n_jobs=-1)
    model.fit(features_df)

    predictions = model.predict(features_df)
    features_df['anomaly_flag'] = predictions
    anomalous_user_ids = features_df[features_df['anomaly_flag'] == -1].index.tolist()

    print(f"Detection complete. Found {len(anomalous_user_ids)} potential anomalies.")
    return anomalous_user_ids, features_df

if __name__ == "__main__":
    transaction_data = fetch_data_from_db(DB_FILE)
    detected_anomalies, features_df = detect_anomalies(transaction_data)

    print("\nSaving feature data and anomaly list for the explainer module...")
    
    # Save the anomalies to CSV
    anomaly_df = pd.DataFrame(detected_anomalies, columns=['anomalous_user_id'])
    anomaly_df.to_csv('detected_anomalies.csv', index=False)
    
    # Save the feature dataframe so the explainer can use it to build baselines
    features_df.to_csv('features_data.csv')

    print("Anomaly Detection Completed")
