import streamlit as st
import pandas as pd
from address_lookup import geocode_address, generate_addresses_to_csv

st.title("NJ Address Generator and Validator")

# Sidebar for generating addresses
with st.sidebar:
    st.header("Generate Addresses")
    num_addresses = st.number_input(
        "Number of addresses to generate", min_value=1, value=10
    )
    if st.button("Generate Addresses"):
        generate_addresses_to_csv(num_addresses)
        st.success(f"Generated {num_addresses} addresses to generated_addresses.csv")

# Main content area
st.header("Address Validation")

# Input method selection
input_method = st.radio(
    "Choose input method", ["Single Address", "Upload CSV", "Use Generated Addresses"]
)

if input_method == "Single Address":
    # Single address input
    address = st.text_input("Enter an address to validate:")
    if st.button("Check Address") and address:
        with st.spinner("Checking address..."):
            result = geocode_address(address)
            if result:
                st.subheader("Results")
                st.write("Input:", address)
                st.write("Best Match:", result["matched_address"])
                st.write(f"Coordinates: ({result['latitude']}, {result['longitude']})")

                if len(result["all_matches"]) > 1:
                    st.subheader("All Matches")
                    for match in result["all_matches"]:
                        with st.expander(f"Match (Score: {match['score']})"):
                            st.write("Address:", match["address"])
                            st.write("Type:", match["match_type"])
                            st.write(
                                f"Coordinates: ({match['latitude']}, {match['longitude']})"
                            )
            else:
                st.error("No matches found for this address")

elif input_method == "Upload CSV":
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if "full_address" in df.columns:
            addresses = df["full_address"].tolist()
        else:
            st.error("CSV must contain a 'full_address' column")
            st.stop()

        if st.button("Check Addresses"):
            results = []
            progress_bar = st.progress(0)

            for i, addr in enumerate(addresses):
                result = geocode_address(addr)
                if result:
                    results.append(
                        {
                            "input": addr,
                            "matched": result["matched_address"],
                            "latitude": result["latitude"],
                            "longitude": result["longitude"],
                            "score": result["all_matches"][0]["score"]
                            if result["all_matches"]
                            else None,
                        }
                    )
                else:
                    results.append(
                        {
                            "input": addr,
                            "matched": "No match",
                            "latitude": None,
                            "longitude": None,
                            "score": None,
                        }
                    )
                progress_bar.progress((i + 1) / len(addresses))

            # Create DataFrame and set proper data types
            results_df = pd.DataFrame(results)
            results_df["latitude"] = pd.to_numeric(
                results_df["latitude"], errors="coerce"
            )
            results_df["longitude"] = pd.to_numeric(
                results_df["longitude"], errors="coerce"
            )
            results_df["score"] = pd.to_numeric(results_df["score"], errors="coerce")

            # Display the results
            st.dataframe(results_df)

            # Download button for results
            csv = results_df.to_csv(index=False)
            st.download_button(
                "Download Results",
                csv,
                "address_results.csv",
                "text/csv",
                key="download-csv",
            )

else:  # Use Generated Addresses
    try:
        df = pd.read_csv("generated_addresses.csv")
        if st.button("Check Generated Addresses"):
            results = []
            progress_bar = st.progress(0)

            for i, row in df.iterrows():
                result = geocode_address(row["full_address"])
                if result:
                    results.append(
                        {
                            "input": row["full_address"],
                            "matched": result["matched_address"],
                            "latitude": result["latitude"],
                            "longitude": result["longitude"],
                            "score": result["all_matches"][0]["score"]
                            if result["all_matches"]
                            else None,
                        }
                    )
                else:
                    results.append(
                        {
                            "input": row["full_address"],
                            "matched": "No match",
                            "latitude": None,
                            "longitude": None,
                            "score": None,
                        }
                    )
                progress_bar.progress((i + 1) / len(df))

            # Create DataFrame and set proper data types
            results_df = pd.DataFrame(results)
            results_df["latitude"] = pd.to_numeric(
                results_df["latitude"], errors="coerce"
            )
            results_df["longitude"] = pd.to_numeric(
                results_df["longitude"], errors="coerce"
            )
            results_df["score"] = pd.to_numeric(results_df["score"], errors="coerce")

            # Display the results
            st.dataframe(results_df)

            # Download button for results
            csv = results_df.to_csv(index=False)
            st.download_button(
                "Download Results",
                csv,
                "address_results.csv",
                "text/csv",
                key="download-csv",
            )
    except FileNotFoundError:
        st.error(
            "No generated addresses found. Please generate addresses first using the sidebar."
        )
