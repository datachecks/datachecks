import React from "react";
import styles from "./Preview.module.css";
import { DashboardMetricOverview } from "../../api/Api";
import { IconButton, Tab, Tabs } from "@mui/material";
import PieChart from "../Piechart";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { BootstrapTooltip } from "../BootstrapTooltip";
import { VerticalTabsProps, docRedirects } from "../../types/component.type";
import { themeColors } from "../../utils/staticData";

interface IOverviewProps {
  dashboard: DashboardMetricOverview;
  width: number;
}

const Overview: React.FC<IOverviewProps> = ({ dashboard, width }) => {
  const [value, setValue] = React.useState(0);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  interface ITabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
  }

  const TabPanel: React.FC<ITabPanelProps> = ({ children, index, value }) => {
    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`vertical-tabpanel-${index}`}
        aria-labelledby={`vertical-tab-${index}`}
      >
        {value === index && (
          <div>
            <p>{children}</p>
          </div>
        )}
      </div>
    );
  };

  function a11yProps(index: number) {
    return {
      id: `vertical-tab-${index}`,
      "aria-controls": `vertical-tabpanel-${index}`,
    };
  }

  return (
    <div className={styles.card}>
      <div className={styles.cardInfo}>
        <h1 className={styles.header}>Overview</h1>
        <p className={styles.description}>
          Key metrics providing insights into the integrity and uniqueness of
          your data.
        </p>
      </div>
      <div className={styles.snapscoreMain}>
        <div className={styles.verticalTabs}>
          <Tabs
            {...VerticalTabsProps}
            orientation="vertical"
            variant="scrollable"
            indicatorColor="primary"
            value={value}
            textColor="inherit"
            onChange={handleChange}
          >
            {Object.entries(dashboard)
              .filter(([dataKey]) => dataKey !== "overall")
              .map(([metric_type, metric], index) => (
                <Tab
                  label={metric_type}
                  aria-label={metric_type}
                  key={metric_type}
                  sx={{ textTransform: "capitalize" }}
                  {...a11yProps(index)}
                />
              ))}
          </Tabs>
        </div>
        <div className={styles.metricsGraph}>
          {Object.entries(dashboard)
            .filter(([dataKey]) => dataKey !== "overall")
            .map(([metric_type, metric], index) => {
              const data = [
                {
                  id: "Unchecked",
                  label: "Unchecked Metrics",
                  value: metric.metric_validation_unchecked,
                  color: themeColors.unchecked,
                },
                {
                  id: "Success",
                  label: "Validation Success",
                  value: metric.metric_validation_success,
                  color: themeColors.success,
                },
                {
                  id: "Failed",
                  label: "Validation Failure",
                  value: metric.metric_validation_failed,
                  color: themeColors.failed,
                },
              ];

              return (
                <TabPanel value={value} index={index}>
                  <div className={styles.metricGraph}>
                    <div
                      style={{
                        position: "absolute",
                        top: "10px",
                        right: "30px",
                        zIndex: 10,
                      }}
                    >
                      <IconButton
                        onClick={() =>
                          window.open(
                            docRedirects.find(
                              (item) => item.key === metric_type
                            )?.url
                          )
                        }
                      >
                        <BootstrapTooltip
                          title={
                            docRedirects.find(
                              (item) => item.key === metric_type
                            )?.info
                          }
                        >
                          <InfoOutlinedIcon
                            fontSize={"small"}
                            style={{
                              opacity: "0.5",
                            }}
                          />
                        </BootstrapTooltip>
                      </IconButton>
                    </div>
                    <PieChart
                      data={data}
                      metricName={metric_type}
                      key={width}
                    />
                  </div>
                </TabPanel>
              );
            })}
        </div>
      </div>
    </div>
  );
};

export default Overview;
